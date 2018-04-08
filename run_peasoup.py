import os

with open('dwf_8bit.txt') as fh:
    lines = fh.readlines()

for ll in lines:
    ll = ll.strip()
    lout = ll[:-14]

    do_str = 'peasoup -p -i %s -o %s --acc_tol 1.25 --acc_start -300 --acc_end 300 --dm_start 1 --dm_end 2000' % (ll, lout) 

    print do_str
    os.system(do_str)
