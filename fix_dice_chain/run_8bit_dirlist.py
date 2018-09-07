import os

#dirin   = '/datax/collate'
dirin   = '/datax2/collate'
#dirout  = '/mnt_bls3/datax3/holding_8bit'
dirout = '/datax3/holding_8bit'
dirlist = os.listdir(dirin)
n_parallel  = 2

for dirname in dirlist:
    dpath = os.path.join(dirin, dirname)
    os.system('./parkes_chain_8bit_batch.py %s %s -n %i'%(dpath, dirout, n_parallel))

