#!/usr/bin/env python
"""
# turboseti_batch.py

Run turboSETI in batch mode.
"""
from batch import *
import time
import random

def run_turboseti(outdir, filename):
    """ Tiddalik subprocess launcher for turboSETI
    
    Args:
        outdir (str): output directory for candidates
        filename (str): filename to read

    Notes:
        This uses a .lock file to designate that processing of the
        input file has started (or is complete).
    """
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
    # Setup Argument parsing from defaults
    import os
    parser = default_argparser(ext='0000.fil')
    args = parser.parse_args()    
    
    # Generate file list from glob
    search_str = os.path.join(args.indir, '*.%s' % args.extension)
    filelist = glob.glob(search_str)
    out_filelist = [args.outdir for ii in range(len(filelist))]
    
    print("Search path: %s " %search_str)
    print("Number of matching files: %s" % len(filelist))

    run_parallel(run_turboseti, (out_filelist, filelist), n_workers=args.nparallel)
   
