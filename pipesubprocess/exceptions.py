import logging
import subprocess
import shlex
import signal

logger = logging.getLogger(__name__)

class PipeSubprocessError(subprocess.SubprocessError):
    '''
    It's a base exception class of pipesubprocess
    '''
    def __init__(self, popen_args, stdout=None, stderr=None):
        self.popen_args = popen_args
        self.stdout = stdout
        self.stderr = stderr

    @property
    def output(self):
        return self.stdout


class TimeoutExpired(PipeSubprocessError):
    '''
    Raised when timeout expired for run(), communicate(), or wait()
    '''
    def __init__(self, popen_args, timeout, stdout=None, stderr=None):
        super().__init__(popen_args, stdout=stdout, stderr=stderr)
        self.timeout = timeout

    def __repr__(self):
        cmds_string = [pa.name for pa in self.popen_args].join(' | ')
        return f'Commands: "{cmds_string}" timed out after {self.timeout} seconds.'

