"""
# tasks.py

Tiddalik tasks for celery 
"""

import time
import os
import glob

import config
from config import app
from singularity import singularity_exec, singularity_run

def dispatch_to_node(taskfn, node_id, args=None, kwargs=None):
    """ Run a task on a given node via celery

    Args:
        taskfn (app.task): A function decorated with celery's @app.task
        node_id (str): Hostname on which to run the task
        args (list): List of arguments to pass to the taskfn
    """
    d = taskfn.apply_async(args=args, kwargs=kwargs, queue=node_id, routing_key='{node_id}.run'.format(node_id=node_id))
    return d


@app.task
def call_singularity(echo_str):
    retcode = singularity_exec("echo {ee}".format(ee=echo_str))
    time.sleep(1)
    return retcode


@app.task
def get_filelist(path_to_files, file_ext):
    """ Generate a list of files on which to run 

    Args:
        path_to_files (str): Path to files on the compute node
        file_ext (str): file extension
    """
    fpath = os.path.join(path_to_files, '*.{ext}'.format(ext=file_ext.strip('.')))
    filelist = glob.glob(fpath)
    return filelist

@app.task
def compress_htr_data(filename_in):
	""" Run compress HTR data pipeline """
	img = '/home/obs/tiddalik/celery/apps/convert_htr_data/convert_htr.simg'
	args_str = '{filename} -qdD'.format(filename=filename_in)
	retcode = singularity_run(args_str, img=img)
	return retcode	

def gather_filelists(path_to_files, file_ext, timeout=10):
    """ Gather filelists from all nodes

    Uses get_filelist task.
    """
    dd = {}
    for node in config.nodes:
        dd[node] = dispatch_to_node(get_filelist, node, args=(path_to_files, file_ext))
    
    cnt = 0.0
    for node, ret in dd.items():
        while ret.status != 'SUCCESS' and cnt <= timeout:
            time.sleep(0.1)
            cnt += 0.1
        dd[node] = ret.result
    if cnt > timeout:
        print("Warning: one or more nodes did not return a file listing.")
    return dd


def test_singularity_all_nodes(file_dict):
	for node, filelist in file_dict.items():
		print("Dispatching to {node}".format(node=node))
		for filename in filelist:
			dispatch_to_node(call_singularity, node, [filename])
	 

if __name__ == "__main__":
	
	d = dispatch_to_node(compress_htr_data, 'blc01', args=['filename_test'])
	
	print("Waiting for task to complete...")
	while d.status == 'PENDING':
		time.sleep(0.5)	
	print(d.result)
	# d = gather_filelists('/datax/PKSMB/GUPPI', '0002.fil')
	# test_singularity_all_nodes(d)

