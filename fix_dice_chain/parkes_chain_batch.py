#!/usr/bin/env python
from __future__ import print_function # Only Python 2.x
import concurrent.futures
import subprocess
import sys
import time
import glob
import itertools
import blimpy as bl

def is_10cm_data(filename):
    a = bl.Waterfall(filename, load_data=False)
    f0 = a.header['fch1'] 
    print(f0)

    if 2500 < f0 < 3500:
        return True
    else:
        return False

def run_parkes_chain(outdir, filename):
    if is_10cm_data(filename): 
        execute(["./parkes_chain %s %s" % (filename, outdir)])
    else:
        print("WARNING: %s is not 10CM data, skipping..." % filename)
    time.sleep(0.01)

def execute(command):
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

if __name__ == "__main__":
    import os
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("indir", help="Input directory to read from")
    parser.add_argument("outdir", help="Output directory to write to")
    parser.add_argument("-e", "--extension", help="extension to look for. Default 0000.fil", 
                        default='0000.fil')
    parser.add_argument("-n", "--nparallel", help="Number of files to process in parallel. Default 1",
                       type=int, default=1)
    args = parser.parse_args()

    search_str = os.path.join(args.indir, '*.%s' % args.extension)
    filelist = glob.glob(search_str)

    with concurrent.futures.ProcessPoolExecutor(max_workers=args.nparallel) as executor:
         result = executor.map(run_parkes_chain, itertools.repeat(args.outdir), filelist)

