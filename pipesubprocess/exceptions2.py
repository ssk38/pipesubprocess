class CalledProcessError(PipeSubprocessError):
    '''
    Raised when run(check=True) is executed and exit with non-zero return code.
    '''
    def __init__(self, popen_args, returncodes, stdout=stdout, stderr=None):
        super().__init__(popeon_args, stdout=stdout, stderr=stderr)
        self.returncodes = returncodes

    def __str__(self):
        ret_str = None
        for i in range(len(self.returncodes)):
            ret = self.returncodes[i]
            pa = self.popen_args[i]
            if ret and ret < 0:
                try:
                    s = f"'{pa.name}' died with {signal.Signals(-ret)}."
                except ValueError:
                    s = f"'{pa.name}' died with signal {-ret}."
            else:
                s = f"'{pa.name}' exited with {ret}"
            if ret_str:
                ret_str += f' {s}'
            else:
                ret_str = s
        return ret_str
