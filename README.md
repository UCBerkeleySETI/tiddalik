# tiddalik
Parkes multi-node processing pipelines

![](http://blogtimewithcarlos.weebly.com/uploads/5/8/3/5/58354427/3419011_orig.jpg)

## Overview

Tiddalik is a simple all-Python code to do run batch processing across nodes, where a
single executable is run on different files in parallel (i.e. 'trivially/pleasingly' parallel). 
The executable can be any bit of code that you can call from bash with command line arguments.

Tiddalik uses:
* Python `subprocess` to execute a desired bash command.
* Python `concurrent.futures` to execute things in parallel. 
* Python `fabric` to run commands across nodes.

Your data should be spread across nodes, in similar directory structures (e.g. in /datax/my_data or /nfs/my_data).

### Helper functions

The three main functions used are defined in `batch.py`. These are:

#### 1. sp_execute: Run a bash command
```python
def sp_execute(command):
    """ Execute a BASH command using python subprocess
    For use with concurrent.futures (parallel processing)
    Continually prints output of stdout to screen.
    Args:
        command (list): Command to execute, wrapped in brackets eg  ['echo hello']
    """
```
Example usage 
```python
sp_execute(["echo %s %s" % ("Hello", "World")])
```

#### 2. run_parallel: Run a function with different args in parallel
```python
def run_parallel(function, args, n_workers=2):
    """ Run a function with different args in parallel 
    
    Wrapper for concurrent.futures executor.
    Args:
        function: Python function to run. See run_echo above as example.
        args [list]: An iterable list of all arguments. The length of the list
                     determines how many times the function is repeated. Each
                     iteration requires its own arguments e.g. 
                     [['filename0', 'filename0_out'], 
                      ['filename1', 'filename1_out']]
        n_workers (int): Number of workers to use (run in parallel).
    """
```

Example usage:
```python
def run_echo(name):
    """ Simple example of using sp_execute """
    sp_execute(["echo Hello %s" % name])

namelist = ["Danny", "Dave", "Darren", "Damien"]
run_parallel(run_echo, namelist, n_workers=8)
```

#### 3. default_argparser: A generic argparse to help out

```python
def default_argparser(ext='fil'):
    """ Default argparser for batch scripts 
    Returns an argparser with input directory, output directory, file extension
    to search for, and number of parallel processes to launch.
    """
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("indir", help="Input directory to read from")
    parser.add_argument("outdir", help="Output directory to write to")
    parser.add_argument("-e", "--extension", help="extension to look for. Default %s" % ext, 
                        default=ext)
    parser.add_argument("-n", "--nparallel", help="Number of files to process in parallel. Default 1",
                       type=int, default=1)
    return parser
```

### Basic recipe

1. Create a file called `TTR_batch.py`, where TTR is the Thing To Run.
2. Create a function called `def run_TTR(outdir, filename)`, which calls `sp_execute(TTR)`
3. In the `__main__` of `TTR_batch.py` setup your argparser and a call to `run_parallel(run_TTR)`, probably using `glob` to make a list of files for the `def run_TTR()` function you just wrote.
4. Open up the `fabfile.py` and write a `run_TTR()` function (there's a config.py script that sets up hostnames).
5. Run your TTR with `> fabfile run_TTR` from the head node. 
