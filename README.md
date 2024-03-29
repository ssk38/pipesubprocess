# pipe-subprocess
' Connects input/ouput streams between multiple subprocesses easily just like shell pipe.
' Provides almost the same interface as python subprocess module with some exceptions.

## Install
```shell
pip3 install pipe-subprocess
```

## Quick how to
Just pass commands to run function.

```python
>>> import pipesubprocess as pipesub
>>> result = pipesub.run(["ls /usr/bin/", "grep py", "head -2"], stdout=pipesub.PIPE)
>>> print(result.stdout)
pbcopy
pydoc

# Commands can be written just as *args.

```python
>>> result = pipesub.run("ls /usr/bin/", "grep py", "head -2")
>>> print(result.stdout)
pbcopy
pydoc
```

# run() quick glance.
Use *run()* function to run multiple piped subprocesses. In more complecated case, use pipesubporcess.Popen.

```python
def run(*cmdlist, shlex=True, stdin=None, input=None, stdout=None, stderr=None, capture_output=True, shell=False, cwd=None, timeout=None, check=False, encoding=None, errors=None, text=True, env=None, universal_newlines=None)
```

* It runs multiple process specified in *cmdlist* and connects stdout and stdin in the order of *cmdlist*.
* It returns *CompletedProcess()*
* *input* is written to stdin of the first command.
* When *timeout* ([second] in float) is specified, it raises *pipesubprocess.TimeoutExpired()* when commands takes longer than that timeout.
* If *check=True*, it raises *pipesubprocess.CalledProcessError()* when there is a command with exit code not zero.
' See [README_details.md] for other options.


## class pipesubprocess.PipeSubprocessError
All exceptions of pipesubprocess module inherits this exception. So all exceptions of thie module can be catched by this exception.

## class pipesubprocess.PopenArgs
* It represents the arguments of one process passed to *subproces.Popen().
* *name*
    * name of the argument. The first args by default.
* See [README_details.md] for other attributes.

## class pipesubprocess.CompletedProcess
* The return value from *run()*, representing the finish status of processes.
* *popen_args_list*
    * List of PopenArgs instance.
* *returncodes*
    * List of return codes. None if all commands have not finished yet.
* *stdout*
    * stdout of the last command.
, *stderr*
    * gathred stderr of all the commands.
* *check_returncodes()*
    * raises *pipesubprocess.CalledProcessError()* when *returncodes* have any non-zero status.
    
## class pipesubprocess.TimeoutExpired
* *popen_args*
    * List of PopenArgs instance.
* *timeout*
    * timeout value specified.
* *stdout*
    * stdout of the last command.
* *stderr*
    * gathred stderr of all the commands.




