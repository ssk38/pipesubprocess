# # Using pipe-subprocess module
## Constants
* *pipesubprocess.PIPE*
    * alias of *subprocess.PIPE*
* *pipesubprocess.STDOUT*
    * alias of *subprocess.STDOUT*
* *pipesubprocess.DEVNULL*
    * alias of *subprocess.DEVNULL*

## pipesubprocess.run(*cmdlist, shlex=True, stdin=None, input=None, stdout=None, stderr=None, capture_output=True, shell=False, cwd=None, timeout=None, check=False, encoding=None, errors=None, text=True, env=None, universal_newlines=None)
* **Note** for the *subprocess.run()* user. The default behavior is different from *subporcess.run()* in the points below:
    * text is True. The type of stdin/stdout is normal string, not byte string.
    * shlex option is introduced. One args of cmdlist can be normal command line with spaces.
    * capture_output is True. Outputs are captured by default.
' *cmdlist*
    * It can take one of the types below:
        * List of command line string. Each string is valid command line. The command line is splitted by *shlex.split()* by default. See shlex option argument.
        * List of list of string. Each list of string is valid args for *subprocess.Popen()*
* *shlex (default:True)*
    * If True, args are parsed by shlex.split()
* *stdin (default:None)*
    * Input stream connected to the stdin of the first command.
    * Specifiy one of the value below:
        * File-like object
        * *pipesubprocess.PIPE*
        * When *input* is specified, it set to *pipesubprocess.PIPE*. No other value can be specified.
* *input (default:None)*
    * input data pushed to stdin.
    * In text mode, it must be normal string. In binary mode, it must be byte code array
* *stdout (default:None)*
    * Output stream connected to the stdout of the last command.
    * Specifiy one of the value below:
        * File-like object
        * *pipesubprocess.PIPE*
        * When capture_output is True, it set to PIPE.
        * When None, stdout is connected to current stdout.
* *stderr (default:None)*
    * Output stream connected to the stdout of the last command.
    * Specifiy one of the value below:
        * File-like object
        * *pipesubprocess.PIPE*
        * *pipesubprocess.STDOUT*
            * stderr is merged to stdout
        * When capture_output is True, it set to PIPE.
        * When None, stderr is connected to current stderr.
* *capture_output (default:True)*
    * stdout and stderr is captured.
* *shell (default:False)*
    * It directory passed to internal call of *subprocess.Popen()* for all processes.
    * If you don't like shlex.split() but command line need to be parsed, use it.
* *cwd (default:None)*
    * It directory passed to internal call of *subprocess.Popen()* for all processes.
    * Working directory is changed to this path before execution.
* *timeout (default:None)*
    * When specified, *pipesubprocess.run()* raises *pipesubprocess.TimeoutExpired()* exception if the processes takes more then timeout seconds to finish.
    * Specify float value as seconds.
    * Specify float value as seconds.
* *encoding (default:None)*
    * It directory passed to internal call of *subprocess.Popen()* for all processes.
* *errors (default:None)*
    * It directory passed to internal call of *subprocess.Popen()* for all processes.
* *text (default:True)*
    * It directory passed to internal call of *subprocess.Popen()* for all processes.
    * If False, stdin/stdout/stderr take the type of  bytecode array.
* *env (default:None)*
    * It directory passed to internal call of *subprocess.Popen()* for all processes.
* *check (default:False)*
    * When True, *pipesubprocess.run()* raises *pipesubprocess.CalledProcessError()* exception if there is any process finished with non-zero status..

# Advanced usage of pipesubprocess
The *subprocess.Popen()* interface is seprated to two classes. First class *PopenArgs* takes per command arguments. Second class *Popen*, the same name as *subprocess.Popen*, takes arguments for all pipe-connected processes.

## pipesubprocess.PopenArgs(args, bufsize=-1, executable=None, stderr=None, preexec_fn=None, close_fds=True, shell=False, cwd=None, env=None, startupinfo=None, creationflags=0, restore_signals=True, start_new_session=False, pass_fds=(), name=None)
* *name (default+None)*
    * It's set to Popen class attribute to distinguish them.
    * If None, it's calculated from args.
* *stderr (default:None)*
    * Use it  when the stderr of specific process is needed. Otherwide, stderr argument specified in *pipesubprocess.Popen()* is used.
    * The value is directory passed to internal call of *subprocess.Popen()*.
* Other arguments are directory passed to internal call of *subprocess.Popen()*.

## pipesubprocess.Popen(popen_args_list, stdin=None, stdout=None, stderr=None, universal_newlines=None, encoding=None, errors=None, text=None, _debug_communicate_io=False))
* *popen_args_list*
    * The array of *pipesubprocess.PopenArgs()*
    * The pipes are formed in the order of this array.
* *stdin*
    * It is connected to the stdin of first command.
    * If *pipesubprocess.PIPE* is specified, *stdin* of the returned Popen instance can be used as stdin input stream.
* *stdout*
    * It is connected to the stdout of last command.
    * If *pipesubprocess.PIPE* is specified, *stdout* of the returned Popen instance can be used as stdout output stream.
* *stderr*
    * It is connected to the stderr of last command.
    * If *pipesubprocess.PIPE* is specified, *stderr* of the returned Popen instance can be used as stderr output stream.
* Other arguments are directory passed to internal call of *subprocess.Popen()*.
    * When one of *universal_newlines*, *encoding*, *erros*, *text* is True, the input/output type is normal string, otherwise byte-code array.
* *pipesubprocess.Popen* supports "with" expression.
* *pipesubprocess.Popen.poll()*
    * Check if child processes have completed.
    * Returns the array of returncode when all processes have completd.
    * Returns None otherwise.
* *pipesubprocess.Popen.wait(timouet=None)*
    * wait the completion of all child processes.
    * If timeout is specified and takes more than the time, it raises *pipesubprocess.ExpiredTimeout()* exception.
    * Returns the array of returncode when all processes have completd.
* *pipesubprocess.Popen.communicate(input=None, timeout=None)*
    * It waits for completion of child processes and returns output as *tuple(outs, errs)*
    * If timeout is specified and takes more than the time, it raises *pipesubprocess.ExpiredTimeout()* exception.
* *pipesubprocess.Popen.kill(*args*)*
    * Sends SIGKILL signal to specified process.
    * Specify the array index of popen_args_list.
    * If no argument specified, sends singal to all processes.
* *pipesubprocess.Popen.terminate(*args*)*
    * Sends SIGINT signal to specified process.
    * Specify the array index of popen_args_list.
    * If no argument specified, sends singal to all processes.
* *pipesubprocess.Popen.send_signal(signal, *args*)*
    * Sends specified signal to specified process.
    * Specify the array index of popen_args_list.
    * If no argument specified, sends singal to all processes.
* *pipesubprocess.Popen.popen_args_list*
    * PopenArgs array specified in constructor.
* *pipesubprocess.Popen.pids*
    * PID array.
    * The index of the array corresponds to popen_args_list
* *pipesubprocess.Popen.returncodes*
    * Return code array.
    * Poplurated only when all processes completed.
    * The index of the array corresponds to popen_args_list
* *pipesubprocess.Popen.outs*
    * stdout string.
    * Used when stdout=PIPE is specified and communicate() is called.
* *pipesubprocess.Popen.errs*
    * stder string.
    * Used when stderr=PIPE is specified in Popen and communicate() is called.
* *pipesubprocess.Popen.stdin*
    * Input stream of the first process.
    * Not None when stdin=PIPE is specified
* *pipesubprocess.Popen.stdout*
    * Output stream of the last process.
    * Not None when stdout=PIPE is specified
* *pipesubprocess.Popen.stderr*
    * Output stream of all the processes.
    * Not None when stderr=PIPE is specified
