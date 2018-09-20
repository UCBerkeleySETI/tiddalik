#!/usr/bin/env python
"""
# tasks.py

Tiddalik tasks for celery 
"""

import time
import os
import glob

from tasks import *

def run_raw_2b_extract_all_nodes(path_to_files, file_ext):
    file_dict = gather_filelists(path_to_files, file_ext)
    
    d_out = []
    for node, filelist in file_dict.items():
        print("Dispatching to {node}".format(node=node))
        if filelist is not None:
            print("Dispatching {i} jobs...".format(i=len(filelist)))
            for filename in filelist:
                if int(node[-1]) % 2 == 1:
                    f0 = 1420.5
                else:
                    f0 = 1324.28
                d = dispatch_to_node(run_2b_extract, node, args=[filename, f0])
                d_out.append(d)
        else:
            print("Warning: no files in filelist, skipping")
    return d_out

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description='Run post-observation compression on hi-time-res (HTR) data')
    p.add_argument('path_to_files', help='Path in which to search for files')
    p.add_argument('-e', '--extension', help='File extension to search for', default='.0000.raw')
    args = p.parse_args()
    
    run_raw_2b_extract_all_nodes(args.path_to_files, args.extension)
            
