#!/usr/bin/env python

import glob
import os
import time
import blimpy as bl

SINGULARITY = '/usr/local/singularity/bin/singularity'
EXE = '~/tiddalik/compress_psr_stokes/convert_htr_data.py'
IMG_PATH = '/opt/singularity/psrkit.simg'

if __name__ == "__main__":
    dl = ('/datax/PKSMB', '/datax', '/datax2', '/datax2/PKSMB')

    for dn in dl:
        dirlist = sorted(glob.glob(os.path.join(dn, '*/')))
        print"%s: %i PKS subdirs" % (dn, len(dirlist))
        
        for dirname in dirlist:
            print('\n------------------')
            print(' Scanning %s        ' % dirname)
            print('-------------------')
            fl = sorted(glob.glob(os.path.join(dirname, '*.0001.fil')))
            
            print('Number of files: %i' % len(fl))
            time.sleep(0.25)

            for ii, filename_in in enumerate(fl):
                print('\n------------------')
                print('[%i / %i]' % ((ii+1), len(fl)))
                print('-------------------')
                fh = bl.Waterfall(filename_in, max_load=0)
                n_int = fh.n_ints_in_file
                n_ifs = fh.header['nifs']
                t_samp = fh.header['tsamp']
                print("File:  %s" % filename_in)
                print("NIFS:  %i" % n_ifs)
                print("TSAMP: %2.6f" % t_samp)
                print("NINT:  %i" % n_int)

                if n_ifs == 4 and t_samp < 0.001 and n_int > 1024:
                    print('%s exec --bind /datax %s %s %s -qdD' % (SINGULARITY, IMG_PATH, EXE, filename_in))
                    os.system('%s exec --bind /datax %s %s %s -qdD' % (SINGULARITY, IMG_PATH, EXE, filename_in))
                else:
                    print("Skipping %s, not a fullstokes HTR product" % filename_in)
                time.sleep(0.5)    
