#!/usr/bin/env python
"""
# batch.py

Tools for batch processing in Python. Used in tiddalik software pipeline.

"""

from __future__ import print_function # Only Python 2.x
import concurrent.futures
import subprocess
import sys
import time
import glob
import itertools

def sp_execute(command):
    """ Execute a BASH command using python subprocess

    For use with concurrent.futures (parallel processing)
    Continually prints output of stdout to screen.

    Args:
        command (list): Command to execute, wrapped in brackets eg  ['echo hello']
    """
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # Poll process for new output until finished
        while True:
            nextline = process.stdout.readline()
            if nextline == '' and process.poll() is not None:
                break
            sys.stdout.write(nextline)
            sys.stdout.flush()

        output = process.communicate()[0]
        exitCode = process.returncode

        if (exitCode == 0):
            return output
        else:
            raise ProcessException(command, exitCode, output)
    except:
        print("FAILED")
        raise

def run_echo(outdir, filename):
    """ Simple example of using sp_execute """
    sp_execute(["echo %s %s" % (filename, outdir)])
    time.sleep(0.1)


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
    with concurrent.futures.ProcessPoolExecutor(max_workers=n_workers) as executor:
        result = executor.map(function, *args)


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


if __name__ == "__main__":
    import os
    parser = default_argparser() 
    args = parser.parse_args()

    search_str = os.path.join(args.indir, '*.%s' % args.extension)
    filelist = glob.glob(search_str)
    print(search_str)
    out_filelist = [args.outdir for ii in range(len(filelist))]
    print(filelist)

    run_parallel(run_echo, (out_filelist, filelist), n_workers=args.nparallel)
    
    #with concurrent.futures.ProcessPoolExecutor(max_workers=args.nparallel) as executor:
    #     result = executor.map(run_parkes_chain, itertools.repeat(args.outdir), filelist)

