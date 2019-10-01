'''
This is truncate_fil_name_tm.py
This file will truncate a bl fil file so that it start with guppi...
This is so the outside_pipe_tm/main_pipe_tm script will have a unifrom output
'''

import os
import sys
import glob


############################################################
# Arguments

input_dir = sys.argv[1]


###########################################################
# Run through files and cut off all before guppi

for input_file in os.listdir(input_dir):
    if input_file is glob.glob(".fil"):
        input_file = str(input_file)
        input_file.split("g")
        output_file = input_file.split("g"[1])
#        new_output_file = 'g' + str(input_file.split("g")[1])
    os.system("mv {0} {1}".format(input_file, str('g' + str(input_file.split("g")[1])))) 
#    print('g' + str(input_file.split("g")[1]))

'''
#This part gets the file name without guppi_

for input_file in os.listdir(input_dir):
    if input_file is glob.glob(".fil"):
        input_file = str(input_file)
        input_file.split("guppi_")
        output_file = input_file.split("guppi_")[1]
    print(str(input_file.split("guppi_")[1]))
'''
