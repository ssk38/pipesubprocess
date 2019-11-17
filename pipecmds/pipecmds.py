#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

import logging
import os
import subprocess
import threading
import time


'''These are the aliases of subprocess'''
PIPE = -1
STDOUT = -2
DEVNULL = -3

class PopenArgs:
    '''
    The possible arguments are Popen arguments except for
    stdin/stdout and name. name is set to popen object.
    This parameter is used to call pipecmds.Popen.
    stdin and stdout are ignored when piped to another process.
    '''
    def __init__(self, args, bufsize=-1, executable=None, stderr=None, preexec_fn=None, close_fds=True, shell=False, cwd=None, env=None, startupinfo=None, creationflags=0, restore_signals=True, start_new_session=False, pass_fds=(), name=None):
        self.name = name
        self.args = args
        self.bufsize = bufsize
        self.executable = executable
        self.stderr = stderr
        self.preexec_fn = preexec_fn
        self.close_fds = close_fds
        self.shell = shell
        self.cwd = cwd
        self.env = env
        self.startupinfo = startupinfo
        self.creationflags = creationflags
        self.restore_signals = restore_signals
        self.start_new_session = start_new_session
        self.pass_fds = pass_fds
        if self.stderr == subprocess.PIPE:
            raise NotImplementedError("PIPE cannot be set for stderr.")

    def __repr__():
        return f"<PipeArgs str(self.__dict__)>"

    def __str__():
        from pprint import pformat
        return pformat(self.__dict__, indent=4)




class Popen:
    '''
    It wraps multiple subprocess.popen and provides I/F like subprocess.Popen.
    '''
    polling_interval = 0.1
    '''
    Parameters
    ----------
    popen_args_list
        The list of pipecmds.PopenArgs
    stderr
        Specify One of pipecmds.DEVNULL, pipecmds.STDOUT, or file-like object
    '''
    def __init__(self, popen_args_list, stdin=None, stdout=None, stderr=None, universal_newlines=None, encoding=None, errors=None, text=None):
        self.text = universal_newlines or encoding or errors or text
        self.encoding = encoding
        self.popen_args_list = popen_args_list
        self.processes = []
        self.stdin = None
        self.stdout = None
        self.stderr = None
        self.stderr_write_end = None
        self.outs = None
        self.errs = None
        self._communicate_called = False
        self._workers = {
            "stderr_drainer": None,
            "close_stderr_write_end_worker": None,
            "waiter": None,
            "stdin_worker": None,
            "stdout_worker": None,
            "stderr_worker": None
        }
        self._stop_workers = False


        '''
        Call popen with each popen_args and connect stdout -> stdin
        between subprocesses.
        '''
        # previous stdout goes into current stdin
        prev_out = stdin
        for i in range(len(self.popen_args_list)):
            popen_args = self.popen_args_list[i]
            if i == len(self.popen_args_list) - 1:
                # Last
                _stdout = stdout
            else:
                _stdout = subprocess.PIPE
            args_dict = popen_args.__dict__

            _stderr = args_dict['stderr'] if args_dict['stderr'] else stderr
            del args_dict['stderr']

            name = args_dict['name'] if args_dict['name'] else args_dict['args'][0]
            del args_dict['name']

            p = subprocess.Popen(stdout=_stdout,
                                 stdin=prev_out,
                                 stderr=_stderr,
                                 text=self.text,
                                 encoding=self.encoding,
                                 **args_dict)
            setattr(p, "name", name)
            logging.info(f"Popening({name} {args_dict})")
            if i > 0:
                """
                piped stdout/stdin is connected between subprocesses and used in
                forked sub-processes. We should release them not to prevent pipe close.
                """
                self.processes[-1].stdout.close()
                self.processes[-1].stdout = None

            self.processes.append(p)
            prev_out = p.stdout

        #self._start_pipe_closer()

        if stdin is PIPE:
            self.stdin = self.processes[0].stdin
        else:
            self.stdin = None

        if stdout is PIPE:
            self.stdout = self.processes[-1].stdout
        else:
            self.stdout = None

        if stderr is PIPE:
            logging.debug("stderr is PIPE")
            if len(self.processes) == 1:
                self.stderr = self.processes[0].stderr
            else:
                r, w = os.pipe()
                self.stderr = os.fdopen(r, 'r')
                self.stderr_write_end = os.fdopen(w, 'w')
                self._start_stderr_drainer()
        else:
            self.stderr = None
            self.stderr_write_end = stderr
            if stderr:
                self._start_stderr_drainer()

    def _start_stderr_drainer(self):
        '''
        drain stderr from all sub-processes and gather to one piped stderr
        '''
        def work_drain_stderr(name, stderr, stderr_write_end, text):
            logging.debug(f"stderr_drainer {name} started")
            if text:
                while (not self._stop_workers and
                       not stderr.closed and
                       not stderr_write_end.closed):
                    line = stderr.readline()
                    if not line:
                        break
                    logging.debug(f"stderr-> {line}")
                    stderr_write_end.write(line)
            else:
                while (not self._stop_workers and
                       not stderr.closed and
                       not stderr_write_end.closed):
                    data = stderr.read(4096)
                    if not data:
                        break
                    logging.debug(f"stderr-> {data}")
                    stderr_write_end.write(data)
            logging.debug(f"stderr_drainer {name} finished")

        def work_close_stderr_write_end():
            logging.debug(f"work_close_stderr_write_end started")
            drainers = self._workers["stderr_drainer"]
            while not self._stop_workers:
                alive = False
                for t in drainers:
                    if t.is_alive():
                        alive = True
                        break
                if not alive:
                    break
            logging.debug(f"work_close_stderr_write_end finished")
            self.stderr_write_end.close()

        stderr_drainer = []

        for p in self.processes:
            name=f"{p.name}_stderr_drainer"
            t = threading.Thread(
                target=lambda: work_drain_stderr(name,
                                                 p.stderr,
                                                 self.stderr_write_end,
                                                 self.text),
                name=name)
            t.start()
            stderr_drainer.append(t)

        self._workers["stderr_drainer"] = stderr_drainer

        if self.stderr:
            # We need closer otherwise reader cannot finish reading.
            close_stderr_write_end_worker = threading.Thread(
                target=work_close_stderr_write_end,
                name=name)
            close_stderr_write_end_worker.start()
            self._workers["close_stderr_write_end_worker"] = close_stderr_write_end_worker

    def __enter__(self):
        return self

    def __exit__(self):
        # To support "with pipecmds.Popen() as p:"
        self.wait()

    def poll(self):
        '''
        Check if child process has terminated. Set and return returncode list attribute. Otherwise, returns None.

        Returns
        ----------
        returncode
            list of returncode of subprocesses.
        '''
        self.returncodes = [p.poll() for p in self.processes]
        if None in self.returncodes:
            return None
        return self.returncodes

    def wait(self, timeout=None):
        '''
        Wait for child processes to terminate. Set and return returncode attribute.

        If the process does not terminate after timeout seconds,
        raise a TimeoutExpired exception.
        It is safe to catch this exception and retry the wait.

        Returns
        ----------
        returncodes
            list of returncodes of subprocesses.
        '''
        logging.debug("wait started")
        def work_wait(name, p, timeout):
            logging.debug(f"waiter {name} started")
            ret = p.wait(timeout=timeout)
            logging.debug(f"waiter {name} finished")
            return ret

        waiter = []
        for p in self.processes:
            name = f"{p.name}_waiter"
            t = threading.Thread(
                target=lambda: work_wait(name, p, timeout),
                name=name)

            t.start()
            waiter.append(t)
        self._workers["waiter"] = waiter
        for t in waiter:
            t.join()
        self._workers["waiter"] = None

        returncodes = self.poll()
        if returncodes is None:
            raise subprocess.TimeoutExpired(cmd="pipecmds", timeout=timeout)
        logging.debug("wait finished")
        return returncodes

    def _time_left_sec(self, timeout_at):
        if timeout_at:
            time_left_sec = (timeout_at - datetime.now()).total_seconds()
            if time_left_sec < 0:
                return 0
            else:
                return time_left_sec
        return None

    def get_timeout_at(self, timeout):
        return datetime.now() + timedelta(seconds=timeout)

    def _start_communicate_pipes(self, input=input):
        logging.debug("_start_communicate_pipes called")

        def work_stdin(input=None):
            logging.debug("stdin_worker started")
            start = 0
            step = 4096
            end = start + step
            while not self._stop_workers and not self.stdin.closed:
                if len(input) > end:
                    logging.debug(f"->stdin {input[start:end]}")
                    self.stdin.write(input[start:end])
                else:
                    logging.debug(f"->stdin {input[start:]}")
                    self.stdin.write(input[start:])
                    break
                start += step
                end += step
            self.stdin.close()
            logging.debug("stdin_worker finished")

        def work_stdout():
            logging.debug("stdout_worker started")
            if self.text:
                self.outs = ""
                while not self._stop_workers:
                    line = self.stdout.readline()
                    if not line:
                        logging.debug(f"stdout-> EOF")
                        break
                    logging.debug(f"stdout-> {line}")
                    self.outs += line
            else:
                self.outs = b""
                while not self._stop_workers:
                    data = self.stdout.read(4096)
                    if not data:
                        logging.debug(f"stdout-> EOF")
                        break
                    logging.debug(f"stdout-> {data}")
                    self.outs += data
            logging.debug("stdout_worker finished")

        def work_stderr():
            logging.debug("stderr_worker started")
            if self.text:
                self.errs = ""
                while not self._stop_workers:
                    line = self.stderr.readline()
                    if not line:
                        logging.debug(f"stderr-> EOF")
                        break
                    logging.debug(f"stderr-> {line}")
                    self.errs += line
            else:
                self.errs = b""

                while not self._stop_workers:
                    data = self.stderr.read(4096)
                    if not data:
                        logging.debug(f"stderr-> EOF")
                        break
                    logging.debug(f"stderr-> {data}")
                    self.errs += data
            logging.debug("stderr_worker finished")

        if input and self.stdin:
            stdin_worker = threading.Thread(
                target=lambda: work_stdin(input=input),
                name="stdin_worker")
            stdin_worker.start()
            self._workers["stdin_worker"] = stdin_worker
        elif self.stdin:
            self.stdin.close()

        if self.stdout:
            stdout_worker = threading.Thread(
                target=work_stdout,
                name="stdout_worker")
            stdout_worker.start()
            self._workers["stdout_worker"] = stdout_worker

        if self.stderr:
            stderr_worker = threading.Thread(
                target=work_stderr,
                name="stderr_worker")
            stderr_worker.start()
            self._workers["stderr_worker"] = stderr_worker

    def communicate(self, input=None, timeout=None):
        '''
        Send data to stdin. Read data from stdout and stderr, until end-of-file is reached.
        Wait for process to terminate. The optional input argument should be data to be sent
        to the upper stream child process, or None, if no data should be sent to the child.
        If streams were opened in text mode, input must be a string. Otherwise, it must be bytes.

        Returns
        ----------
        stdout_data
            stdout of down most process
        stderr_data
            stderr of whole process if pipecmds.PIPE is specified.
        The data will be strings if streams were opened in text mode; otherwise, bytes.
        '''
        logging.debug("communicate called")
        if len(self.processes) == 1:
            # In this case, just call subprocess.communicate
            self.outs, self.errs = self.processes[0].communicate(input=input, timeout=timeout)
            return self.outs, self.errs

        firsttime = True
        if self._communicate_called:
            firsttime = False
        self._communicate_called = True

        if firsttime:
            self._start_communicate_pipes(input=input)

        timeout_at = None
        if timeout:
            timeout_at = self.get_timeout_at(timeout)

        self.wait(timeout=timeout)

        # If self.wait() timedout, it raises to caller out of thie method.
        # If we reach here, all processes have finished.
        # Close stdin first then wait for the end of output workers.
        if self.stdin:
            self.stdin.close()

        timedout = False
        if self._workers["stdin_worker"]:
            timeout_left = self._time_left_sec(timeout_at)
            self._workers["stdin_worker"].join(timeout=timeout_left)
            timedout = self._workers["stdin_worker"].is_alive()

        if self._workers["stdout_worker"] and not timedout:
            timeout_left = self._time_left_sec(timeout_at)
            self._workers["stdout_worker"].join(timeout=timeout_left)
            timedout = self._workers["stdout_worker"].is_alive()

        if self._workers["stderr_worker"] and not timedout:
            timeout_left = self._time_left_sec(timeout_at)
            self._workers["stderr_worker"].join(timeout=timeout_left)
            if not timedout:
                timedout = self._workers["stderr_worker"].is_alive()

        if timedout:
            raise subprocess.TimeoutExpired(cmd="pipecmds", timeout=timeout)

        # Guard all workers from running just in case.
        self._stop_workers = True

        # Close up pipes
        if self.stdout:
            self.stdout.close()

        if self.stderr:
            self.stderr.close()

        for p in self.processes:
            if p.stderr:
                p.stderr.close()

        return self.outs, self.errs

    def kill(self):
        for p in self.processes:
            p.kill()

