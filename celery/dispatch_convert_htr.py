#!/usr/bin/env python
"""
# tasks.py

Tiddalik tasks for celery 
"""

import time
import os
import glob

from tasks import dispatch_to_node, compress_htr_data, gather_filelists

def compress_htr_all_nodes(path_to_files, file_ext):
    file_dict = gather_filelists(path_to_files, file_ext)
    
    d_out = []
    for node, filelist in file_dict.items():
        print("Dispatching to {node}".format(node=node))
        for filename in filelist:
            d = dispatch_to_node(compress_htr_data, node, args=[filename])
            d_out.append(d)
    return d_out

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description='Run post-observation compression on hi-time-res (HTR) data')
    p.add_argument('path_to_files', help='Path in which to search for files')
    p.add_argument('-e', '--extension', help='File extension to search for', default='0001.fil')
    args = p.parse_args()
    
    compress_htr_all_nodes(args.path_to_files, args.extension)
            
