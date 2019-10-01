#!/usr/bin/env python

############################################
'''
This is compile_pdfs_tm.py
This script collects all the .pdf outputs in a dir and creates a dir for them.
'''

#############################################
import os
import os, sys
import sys

###############################################
data_dir = sys.argv[1]


###########################################################
# define argument name
data_dir = sys.argv[1]
os.environ['data_dir'] = data_dir

compilation_dir =  datetime.datetime.now().strftime('All_pdfs: %Y-%m-%d_%H-%M-%S')
os.mkdir(compilation_dir)

############################################################
# Function definitions

def move_pdf(pdf_file):
    os.system("mv {0} {1} ".format(pdf_file, compilation_dir)

#############################################################

os.listdir(data_dir)

for f in os.listdir(data_dir):
    if f.endswith(".pdf"):
        pdf_file = f
        move_pdf(pdf_file)
    else:
        continue
