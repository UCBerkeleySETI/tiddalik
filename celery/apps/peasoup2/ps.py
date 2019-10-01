#!/usr/bin/env python

import os
import argparse

# peasoup -v -p -i <input fil file>  --dm_start 0 --dm_end 500 -o <output dir name>  -k <chankill.txt file> -z <birds file>

p = argparse.ArgumentParser(description='Run PEASOUP yo')
p.add_argument('fil', help='Path to filterbank file')
p.add_argument('-o', dest='outdir', default='/datax2/users/tp', help='output directory root')

args = p.parse_args()

fil = args.fil
froot  = fil.replace('.fil', '')
outdir = os.path.join(args.outdir, os.path.basename(froot))


print(outdir)
os.chdir(outdir)

with open(os.path.basename(froot) + ".location", 'w') as locfile:
    locfile.write(args.fil)

hdr_file_name = os.path.basename(froot) + ".header"
hdr_file = open(hdr_file_name, "r")
hdr_data = hdr_file.readlines()
source_name = hdr_data[0].strip("\n")
if source_name == "": source_name = "Unknown"

kill   = '{}_time.kill'.format(source_name)
birds  = '{}.birds'.format(source_name)
cmd = "/home/obs/tiddalik/celery/apps/peasoup2/ps.sh {fil} ./ {kill} {birds}".format(fil=fil, outdir=outdir, kill=kill, birds=birds)

print(cmd)
os.system(cmd)
