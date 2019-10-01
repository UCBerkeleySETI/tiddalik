#!/usr/bin/env python


"""
This pipeline is a pulsar search script
It uses PRESTO and PEASOUP
It is designed to take 8 bit filterbank files 
It conduct the following processes:
RFI mitigation with PRESTO
Search for pulsar candidates usin PEASOUP
and ??
and ??

"""
"""
Example cmd:$ python main_pipe.py <your_filterbank_file.fil>  
"""
# args for rfi_filter_tm.py  -fil <fil_file> -time 10.0 -timesig 5.0 -freqsig 4.0 -chanfrac 0.7 -intfrac 0.3 -max_percent 20.0 -mask -sp

from argparse import ArgumentParser
import xml.etree.ElementTree as ET
import os
import timeit
import sys
import subprocess
import numpy as np
import glob
import fnmatch
import argparse
import sys, os
import errno
import img2pdf
import rfi_quality_check_tm as rfiqul
import rfi_filter_tm as rfifil
import create_bird as cbird
import bird_wrapper
from rfi_filter_tm import rfi_filter

#####################################################################
# input arguments for the script
fil_file = sys.argv[1]
pipe_home = '/datax2/users/mar855/PulsarSearch/'
os.environ['pipe_home'] = pipe_home

'''
drive,path = os.path.splitdrive(fil_file)
path,filename = os.path.split(path)
print('Drive is %s Path is %s and file is %s' % (drive, path, filename))
'''
#####################################################################
# Defining variables

path = './' 
fil_file.split("_")
host = fil_file.split("_")[0]
mjd = fil_file.split("_")[2]
coords = fil_file.split("_")[5]

dir_name = host + '_' + mjd + '_' + coords + '/'

os.environ['dir_name'] = dir_name 
dir_path = path + dir_name
os.environ['dir_path'] = dir_path



##########################################################################
# This checks for the directory named after the fil file and creates one if it can't find it
# This is the folder the ourput files from rfi_fil will go into for each fil file
# This is also where the peasoup candidate xml dir/file will go (This may change dependig on Shi's recommendation).

if not os.path.exists(os.path.dirname(dir_name)):
    try:
        os.mkdir(dir_path)
        print("Successfully created directory %s" % dir_name)
#        os.system('cd $dir_path')
 #       print("Changing directory to %s" % dir_name)
    except OSError as exc: # Guard against race condition
        if exc.errno == errno.EEXIST:
            print("Directory %s already exists" % dir_name)
#        else exc.errno != errno.EEXIST:
#            raise
# Do I need these above two lines?

############################################################################################################
# This changes directory to (new working dir) the dir created for the ourput files to sun rfi_fil there
 
# initial directory 
cwd = os.getcwd()   #current working dir
# dir_path = str(dir_path) #new working dir

try:
    os.chdir(dir_path)
    print("Changing Directory -", os.getcwd())
except OSError:
    raise 


# This part runs rfi_filter_tm on the fil_file and creates folder with _chankil.txt and .birds and other oupur files
cmd = 'python /datax2/users/mar855/PulsarSearch/rfi_filter_tm.py -fil ../{0} -time 10.0 -timesig 5.0 -freqsig 4.0 -chanfrac 0.7 -intfrac 0.3 -max_percent 20.0'.format(fil_file)
print(cmd)
subprocess.call(cmd, shell=True)
# print (cmd)

####################################################################################################3
# This section run PEASOUP using the fil file and the _chankill.txt and .birds file created ase_namebove
# below from rfi_filter_tm.py rfi_filter() 
file_name = fil_file[:-4] #file_name is filterbank file without .fil extension
hdrbase = file_name.split("/")[-1]
hdr_file_name = hdrbase+".hdr" #create name for .hdr file
hdr_file = open(hdr_file_name, "r")
hdr_data = hdr_file.readlines()
source_name = hdr_data[0].strip("\n")
MJD = hdr_data[1].strip("\n").replace(".", "_")
if (len(MJD) - MJD.index("_") - 1) > 4: #check to see if the MJD has more than 4 decimal places
        MJD = MJD[:MJD.index("_") + 5] #reduce the MJD to 4 decimal places
if source_name == "": source_name = "Unknown"
base_name = source_name + "_" + MJD #create a base filename for files that will be created from the pipeline.
bird_file = str(base_name + '.birds')
chan_killfile_name = str(base_name + '_chankill.txt')
mask_file_name = str(base_name + '_rfifind.mask')


peasoup_dir_name = str("PEASOUP_" + base_name)

# Run Peasoup
'''
if os.path.exists(bird_file):
    cmd = 'peasoup -v -p -i ../{0} --dm_start 0 --dm_end 500 -o ./{1} -k {2} -z {3} '.format(fil_file, peasoup_dir_name, chan_killfile_name, bird_file)
    subprocess.call(cmd, shell=True)
    print (cmd)
else:
'''
cmd = 'peasoup -v -p -i ../{0} --dm_start 0 --dm_end 500 -o ./{1} -k {2}'.format(fil_file, peasoup_dir_name, chan_killfile_name)
subprocess.call(cmd, shell=True)
print (cmd)

# This section moves to PEASOUP folder and runs prepfold on the PEASOUP overview.xml file

cwd = os.getcwd()   #current working dir
peasoup_dir = path + peasoup_dir_name 
os.environ['peasoup_dir'] = peasoup_dir

try:
    os.chdir(peasoup_dir)
    print("Changing Directory -", os.getcwd())
except OSError:
    raise

tree = ET.parse('overview.xml')
root = tree.getroot()

for cand in root.findall('candidates/candidate'):
    print cand.tag, cand.attrib
    for node in cand.getiterator():
        if node.tag == 'period':
            period = float(node.text)
        elif node.tag == 'dm':
            dm = float(node.text)
        elif node.tag == 'snr':
            snr = float(node.text)

    if snr >= 10:
        fold_out = fil_file + '_DM' + str(dm) + '_P' + str(period) + '.ps'
        print fold_out
        if period < 0.002:
            Mp, Mdm, N = 2, 3, 24
            npart = 50
            otheropts = " "
        elif period < 0.05:
            Mp, Mdm, N = 2, 1, 50
            npart = 40
            otheropts = "-pstep 1 -pdstep 2 -dmstep 3"
        elif period < 0.5:
            Mp, Mdm, N = 1, 1, 100
            npart = 30
            otheropts = "-pstep 1 -pdstep 2 -dmstep 1"
        else:
            Mp, Mdm, N = 1, 1, 200
            npart = 30
            otheropts = "-nopdsearch -pstep 1 -pdstep 2 -dmstep 1"

            print period, dm, snr

        if os.path.exists(mask_file_name):
            cmd = 'prepfold -noxwin -ncpus 4 -dm {0} -nsub {1} -npart {2} {3} -n {4} -npfact {5} -ndmfact {6} -p {7} -mask ../{8} ../../{9}'.format(dm, 88, npart, otheropts, N, Mp, Mdm, period, mask_file_name , fil_file)
            print period, dm, snr
            print (cmd)
            subprocess.call(cmd, shell=True)

        else:
            cmd = 'prepfold -noxwin -ncpus 4 -dm {0} -nsub {1} -npart {2} {3} -n {4} -npfact {5} -ndmfact {6} -p {7} ../../{8}'.format(dm, 88, npart, otheropts, N, Mp, Mdm, period, fil_file)
            print period, dm, snr
            print (cmd)
            subprocess.call(cmd, shell=True)


#####################################################################################
# This section makes the dir to move png into
os.chdir('../../')


cand_dir = path + 'cands_' + dir_name #+ '/'
os.environ['cand_dir'] = cand_dir
remain_dir = path + 'remain_' + dir_name #+ '/'
os.environ['remain_dir'] = remain_dir



# if not os.path.exists(os.path.dirname(dir_name)):
try:
    os.mkdir(cand_dir)
    print("Successfully created directory %s" % cand_dir)
    os.system('cd $cand_dir')
    print("Changing directory to %s" % cand_dir)
except OSError as exc: # Guard against race condition
    if exc.errno == errno.EEXIST:
        print("Directory %s already exists" % cand_dir)



if os.path.exists(cand_dir):
    try:
        os.system('mv -f *.png $cand_dir')
        print("Moving .png files to %s" % cand_dir)
    except OSError as exc: # Guard against race condition
        if exc.errno == errno.EEXIST:
            print("Failed to move .png files to %s" % cand_dir)


####################################################################
# This section makes the dir for the remaining files to go into


# if not os.path.exists(os.path.dirname(dir_name)):
try:
    os.mkdir(remain_dir)
    print("Successfully created directory %s" % remain_dir)
    os.system('cd $remain_dir')
    print("Changing directory to %s" % remain_dir)
except OSError as exc: # Guard against race condition
    if exc.errno == errno.EEXIST:
        print("Directory %s already exists" % remain_dir)



if os.path.exists(remain_dir):
    try:
        os.system('mv -f *pfd* $remain_dir')
        print("Moving remaining ouput to %s" % remain_dir)
    except OSError as exc: # Guard against race condition
        if exc.errno == errno.EEXIST:
            print("Failed to move files to %s" % remain_dir)

# os.chdir('../')
# print("Changing Directory")
cwd = os.getcwd()
print(cwd)
#####################################################################
# This creates pdf of cands folder
cands_contents = cand_dir + '*'
os.environ['cands_contents'] = cands_contents
pdf_file_name = cand_dir[:-1] + '.pdf'
os.environ['pdf_file_name'] = pdf_file_name

os.system( "img2pdf {0} -o {1}".format(cands_contents, pdf_file_name))
print("Making pdf of candidate plots")
