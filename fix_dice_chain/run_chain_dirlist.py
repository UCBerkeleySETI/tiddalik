import os

dirin   = '/datax/collate'
dirout  = '/datax3/holding'
dirlist = os.listdir(dirin)
n_parallel  = 1

for dirname in dirlist:
    dpath = os.path.join(dirin, dirname)
    os.system('./parkes_chain_batch.py %s %s -n %i'%(dpath, dirout, n_parallel))

