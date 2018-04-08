#!/usr/bin/env python
from batch import *
from fabric.api import *
import time
import random

def run_turboseti(outdir, filename):
    time.sleep(random.random())
    bname = os.path.basename(filename)
    lname = os.path.splitext(bname)[0] + '.lock'
    lname = os.path.join(outdir, lname)
    #lname = os.path,join(outdir, lname)
    if not os.path.exists(lname):
        os.system('touch %s' % lname) 
        print("CMD: turboSETI %s %s -M 4 -s 10 " % (filename, outdir))
        sp_execute(["turboSETI %s -o %s -M 4 -s 10 " % (filename, outdir)])
    time.sleep(random.random())
   

if __name__ == "__main__":
    import os
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("indir", help="Input directory to read from")
    parser.add_argument("outdir", help="Output directory to write to")
    parser.add_argument("-e", "--extension", help="extension to look for. Default h5.fil", 
                        default='0000.h5')
    parser.add_argument("-n", "--nparallel", help="Number of files to process in parallel. Default 1",
                       type=int, default=1)
    args = parser.parse_args()

    # Generate file list from glob
    search_str = os.path.join(args.indir, '*.%s' % args.extension)
    filelist = glob.glob(search_str)
    out_filelist = [args.outdir for ii in range(len(filelist))]
    
    print("Search path: %s " %search_str)
    print("Number of matching files: %s" % len(filelist))

    run_parallel(run_turboseti, (out_filelist, filelist), n_workers=args.nparallel)
   
