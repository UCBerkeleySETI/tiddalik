#!/usr/bin/env python

import glob
import os
import time

SINGULARITY = '/usr/local/singularity/bin/singularity'
EXE = '~/tiddalik/compress_psr_stokes/convert_htr_data.py'
IMG_PATH = '/opt/singularity/psrkit.simg'

if __name__ == "__main__":
    fl = sorted(glob.glob('/datax/PKSMB/GUPPI/*.0001.fil'))
    for ii, filename_in in enumerate(fl):
        print('\n------------------')
        print('[%i / %i]' % ((ii+1), len(fl)))
        print('-------------------')
        print('%s exec --bind /datax %s %s %s -qTdD' % (SINGULARITY, IMG_PATH, EXE, filename_in))
        os.system('%s exec --bind /datax %s %s %s -qTdD' % (SINGULARITY, IMG_PATH, EXE, filename_in))
        time.sleep(0.5)    
