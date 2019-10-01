#!/usr/bin/env python

'''
This is outside_pipe_tm.py
This is a script to automate stages
1. take .fil files from directory
2. run main_pipe_tm.py on them
3. run organise_output_tm.py
mkdir and mv prepfold output into it
'''
'''
Example :$ python outside_pipe.py <dir_with_your_data>
'''

############################################################
'''
You need to go through and deletes the unused modules below
'''
import os
import sys
import subprocess
import glob
import argparse
import sys, os
import errno
# import main_pipe_tm as mpipe


############################################################
# define argument name
data_dir = sys.argv[1] 
os.environ['data_dir'] = data_dir

############################################################
# Function definitions

def main_pipe(fil_file):
    os.system("python /datax2/users/mar855/PulsarSearch/main_pipe_no_birds.py %s" % fil_file) 

'''
def png2pdf(cands_dir):
    for root, dirs, files in os.walk(data_dir):
        for f in files:
            os.system("python /datax2/users/mar855/PulsarSearch/png_to_pdf_tm.py %s" % cands_dir)
'''
#######################################################################
# This section calls functions

for f in os.listdir(data_dir):
    if f.endswith(".fil"):        
        fil_file = f
        main_pipe(fil_file)
    else:
        continue 

'''
for d in data_dir:
    if d is glob.glob("cands_*"):
        png2pdf(cands_dir)
    else:
        continue
'''
