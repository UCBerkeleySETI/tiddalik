#!/usr/bin/env python
"""
# tasks.py

Tiddalik tasks for celery 
"""

import time
import os
import glob

from tasks import dispatch_to_node, run_turboseti, gather_filelists

def run_turboseti_all_nodes(path_to_files, file_ext):
    file_dict = gather_filelists(path_to_files, file_ext)
    
    d_out = []
    for node, filelist in file_dict.items():
        print("Dispatching to {node}".format(node=node))
        if filelist is not None:
            print("Dispatching {i} jobs...".format(i=len(filelist)))
            for filename in filelist:
                outdir = os.path.dirname(filename)
                d = dispatch_to_node(run_turboseti, node, args=[filename, outdir])
                d_out.append(d)
        else:
            print("Warning: no files in filelist, skipping")
    return d_out

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description='Run post-observation turboSETI pipeline on hi-freq res  data')
    p.add_argument('path_to_files', help='Path in which to search for files')
    p.add_argument('-e', '--extension', help='File extension to search for', default='0000.fil')
    args = p.parse_args()
    
    run_turboseti_all_nodes(args.path_to_files, args.extension)
            
