#!/usr/bin/env python
"""
# tasks.py

Tiddalik tasks for celery 
"""

import time
import os
import glob

from tasks import dispatch_to_node, run_tommy_pipe_rfifind, gather_filelists_recursive

def dispatch_run_tommy_pipe_rfifind(path_to_files, file_ext):
    file_dict = gather_filelists_recursive(path_to_files, file_ext)
    
    d_out = []
    for node, filelist in file_dict.items():
        print("Dispatching to {node}".format(node=node))
        if filelist is not None:
            print("Dispatching {i} jobs...".format(i=len(filelist)))
            for filename in filelist:
                outdir = os.path.dirname(filename)
                d = dispatch_to_node(run_tommy_pipe_rfifind, node, args=[filename,])
                d_out.append(d)
        else:
            print("Warning: no files in filelist, skipping")
    return d_out

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description='Run Tommy\'s RFI pipeline on hi-time res data')
    p.add_argument('path_to_files', help='Path in which to search for files')
    p.add_argument('-e', '--extension', help='File extension to search for', default='8b.fil')
    args = p.parse_args()
    
    dispatch_run_tommy_pipe_rfifind(args.path_to_files, args.extension)
