#!/usr/bin/env python
"""
# gen_8bit_batch.py

Use sigproc sum_fil to convert from 32-bit to 8-bit filterbank files
"""

from batch import *
from config import sigproc_sum_fil_path
import os
import glob
import time
import random

SUMFIL_PATH = sigproc_sum_fil_path

def run_peasoup(outdir, filename):
    """ Tiddalik subprocess launcher for peasoup
    
    Args:
        outdir (str): output directory for candidates
        filename (str): filename to read

    Notes:
        This uses a .lock.peasoup file to designate that processing of the
        input file has started (or is complete).
    """
    time.sleep(random.random())
    bname = os.path.basename(filename)
    lname = os.path.splitext(bname)[0] + '.lock.peasoup'
    lname = os.path.join(outdir, lname)
    filename_out = os.path.join(outdir, os.path.splitext(bname)[0] + '.peasoup')
   
    do_str =  'peasoup -p -i %s -o %' % (filename, filename_out)
    do_str += '--acc_tol 1.25 --acc_start -300 --acc_end 300'
    do_str += '--dm_start -2000 --dm_end 2000' 

    if not os.path.exists(lname):
        os.system('touch %s' % lname) 
        print("CMD: %s " % do_str)
        sp_execute([do_str])
    time.sleep(random.random())
   
if __name__ == "__main__":
    # Setup Argument parsing from defaults
    import os
    parser = default_argparser(ext='fil')
    args = parser.parse_args()    
    
    # Generate file list from glob
    search_str = os.path.join(args.indir, '*.%s' % args.extension)
    filelist = glob.glob(search_str)
    out_filelist = [args.outdir for ii in range(len(filelist))]
    
    print("Search path: %s " %search_str)
    print("Number of matching files: %s" % len(filelist))

    run_parallel(run_peasoup, (out_filelist, filelist), n_workers=args.nparallel)

