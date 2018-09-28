#!/usr/bin/env python
"""
# turboseti_batch.py

Run turboSETI in batch mode.
"""

import os

def run_turboseti(filename, outdir):
    """ Tiddalik subprocess launcher for turboSETI
    
    Args:
        outdir (str): output directory for candidates
        filename (str): filename to read

    Notes:
        This uses a .lock file to designate that processing of the
        input file has started (or is complete).
    """
    bname = os.path.basename(filename)
    lname = os.path.splitext(bname)[0] + '.turboseti.lock'
    lname = os.path.join(outdir, lname)
    cname = os.path.splitext(bname)[0] + '.turboseti.complete'
    cname = os.path.join(outdir, cname)
    zname = os.path.splitext(bname)[0] + '.turboseti.failed'
    zname = os.path.join(outdir, zname)
   
    if outdir == '' or outdir is None:
        outdir = bname

    # Make sure output dir ends with trailing slash (turboseti quirk)
    outdir = outdir.rstrip('/') + '/'

    if not os.path.exists(lname):
        os.system('touch %s' % lname) 
        print("RUNNING CMD: turboSETI %s -o %s -M 4 -s 10 " % (filename, outdir))
        retcode = os.system("turboSETI %s -o %s -M 4 -s 10 " % (filename, outdir))
        
        if retcode == 0:
            os.system('touch %s' % cname)   # Completed
        else:
            os.system('touch %s' % zname)   # Failed!
        return retcode
    else:
        print("lock file exists, skipping...")

if __name__ == "__main__":
    import argparse 
    p = argparse.ArgumentParser(description='Ru turboseti on a give file')
    p.add_argument('filename', help='filename of input filterbank file.')
    p.add_argument('-o', '--outputdir', type=str, help='Output directory (default same as input filename)', default='')
    args = p.parse_args()
 
    run_turboseti(args.filename, args.outputdir)
