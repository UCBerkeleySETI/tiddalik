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
LDL = 'LD_LIBRARY_PATH=/usr/local/gcc-5.4/lib64/:/usr/local/cuda-8.0/lib64:/usr/local/lib:/usr/local/hdf5/lib:/usr/local/lib'
DCPY = 'source /home/pri229/tiddalik/env.bash; ' #ri229/urce /opt/pyve/activate dcpy; '
BEAM_MAPPING = beam_mapping   # From config.py

test_dict = {'blc01' : ['a', 'b', 'c'], 'blc02' : [ 'd', 'fu']}

@task
@parallel
@hosts(mb_nodes)#['blc01', 'blc02'])
def run_turboseti():
    indir = '/mnt_bls3/datax3/holding'
    outdir = '/mnt_bls3/datax2/users/pri229/rodeo'
    ext = '0000.h5'
    nparallel = 8
    exe = '/home/pri229/tiddalik/turboseti_batch.py'
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

