#!/usr/bin/env python
"""
# tasks.py

Tiddalik tasks for celery 
"""

import time
import os
import glob

from tasks import *

def upload_to_blpd0_all_nodes(path_to_files, file_ext):
    file_dict = gather_filelists(path_to_files, file_ext)
    prepend_hostname = True
    d_out = []
    for node, filelist in file_dict.items():
        print("Dispatching to {node}".format(node=node))
        if filelist is not None:
            print("Dispatching {i} jobs...".format(i=len(filelist)))
            for filename in filelist:
                d = dispatch_to_node_single_cpu(upload_to_blpd0, node, args=[filename, prepend_hostname])
                d_out.append(d)
        else:
            print("Warning: no files in filelist, skipping")
    return d_out

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description='Upload data in dir with given extension to blpd0')
    p.add_argument('path_to_files', help='Path in which to search for files')
    p.add_argument('-e', '--extension', help='File extension to search for', default='.raw2b')
    args = p.parse_args()
    
    upload_to_blpd0_all_nodes(args.path_to_files, args.extension)
            
