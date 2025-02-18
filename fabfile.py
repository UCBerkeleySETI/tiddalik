"""
fabfile.py
----------
Fabric remote admin and management functions. See README.md for usage
instructions.
"""

import os
import time
import pandas as pd
from fabric.api import *
from fabric.context_managers import hide, show
import glob
from datetime import datetime
from config import *
DCPY = 'source /home/obs/tiddalik/env.bash; ' #ri229/urce /opt/pyve/activate dcpy; '
BEAM_MAPPING = beam_mapping   # From config.py

@task
@parallel
@hosts(mb_nodes)
def run_compress_htr_data():
    """ Convert hi-time res data to 8-bit Stokes-I and archival HDF5 format """
    exe = '/home/obs/tiddalik/compress_psr_stokes/convert_htr_data_batch.py'
    run("%s %s" % (DCPY, exe))

@task
@parallel
@hosts(mb_nodes)#['blc01', 'blc02'])
def run_gen_8bit_pksmb():
    """ Run sumfil 8bitter on Parkes data in /datax/PKSMB/GUPPI """
    indir  = '/datax/PKSMB/GUPPI/'
    outdir = '/datax/PKSMB/GUPPI/'
    ext = '0001.fil'
    nparallel = 1
    exe = '/home/obs/tiddalik/gen_8bit_batch.py'
    #print("%s; %s %s %s %s -e %s -n %i" % (LDL, DCPY, exe, indir, outdir, ext, nparallel))
    run("%s %s %s %s -e %s -n %i" % (DCPY, exe, indir, outdir, ext, nparallel))



@task
@parallel
@hosts(mb_nodes)#['blc01', 'blc02'])
def run_turboseti_pksmb():
    """ Run turboSETI on Parkes data in /datax/PKSMB/GUPPI """
    indir  = '/datax/PKSMB/GUPPI/'
    outdir = '/datax/PKSMB/GUPPI/'
    ext = '0000.fil'
    nparallel = 8
    exe = '/home/obs/tiddalik/turboseti_batch_single_folder.py'
    #print("%s; %s %s %s %s -e %s -n %i" % (LDL, DCPY, exe, indir, outdir, ext, nparallel))
    run("%s %s %s %s -e %s -n %i" % (DCPY, exe, indir, outdir, ext, nparallel))

@task
@parallel
@hosts(mb_nodes)#['blc01', 'blc02'])
def run_turboseti():
    """ Run turboSETI on Parkes data in /datax/ and /datax2/ """
    #indir = '/mnt_bls3/datax3/holding'
    #outdir = '/mnt_bls3/datax2/users/pri229/rodeo'
    #indir  = '/datax/PKSMB/'
    #outdir = '/datax/PKSMB/'
    indirs = ['/datax2/', '/datax2/PKSMB/', '/datax/', '/datax/PKSMB/']
    outdirs = indirs
    #indir  = '/datax2/'
    #outdir = '/datax2/'
    
    for indir, outdir in zip(indirs, outdirs):
        #ext = '0000.fil'
        ext = 'hires.hdf'
        nparallel = 8
        exe = '/home/obs/tiddalik/turboseti_batch.py'
        #print("%s; %s %s %s %s -e %s -n %i" % (LDL, DCPY, exe, indir, outdir, ext, nparallel))
        run("%s %s %s %s -e %s -n %i" % (DCPY, exe, indir, outdir, ext, nparallel))
 
@task
@hosts(mb_nodes)
def mount_storage_nodes():
    """ Mount storage nodes onto compute nodes """
    for node, ipaddr in storage_10gb.items():
        for mnt in storage_mnt_points:
            with warn_only():
                mnt_dir = os.path.join('/mnt_%s' % node, mnt.strip('/'))
                print(mnt_dir)
                sudo("mkdir -p %s" % mnt_dir)
                sudo('mount %s:%s %s' % (ipaddr, mnt, mnt_dir)) 

