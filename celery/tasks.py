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


def dispatch_to_node_priority(taskfn, node_id, args=None, kwargs=None):
    """ Run a task on a given node via celery -- to priority worker

    Args:
        taskfn (app.task): A function decorated with celery's @app.task
        node_id (str): Hostname on which to run the task
        args (list): List of arguments to pass to the taskfn
    """
    q = '{n}_priority'.format(n=node_id)
    rk = '{q}.run'.format(q=q)
    d = taskfn.apply_async(args=args, kwargs=kwargs, queue=q, routing_key=rk)
    return d

def gather_filelists(path_to_files, file_ext, timeout=10):
    """ Gather filelists from all nodes

    Uses get_filelist task.
    """
    dd = {}
    for node in config.nodes:
        dd[node] = dispatch_to_node_priority(get_filelist, node, args=(path_to_files, file_ext))
    
    cnt = 0.0
    for node, ret in dd.items():
        while ret.status != 'SUCCESS' and cnt <= timeout:
            time.sleep(0.1)
            cnt += 0.1
        dd[node] = ret.result
    if cnt > timeout:
        print("Warning: one or more nodes did not return a file listing.")
    return dd
 

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
def run_2b_extract(filename_in, f0=1420.5):
    """ Run SETI@HOME 2-bit extraction code """
    img = 'setiathome/setiathome.simg'
    img = os.path.join(config.SINULARITY_APP_DIR, img)
    fout = os.path.splitext(filename_in)[0] + 'f{f0}.raw2b'.format(f0=f0)
    args_str = '{filename} {f0} {fout}'.format(filename=filename_in, f0=f0, fout=fout)
    retcode = singularity_run(args_str, img=img)
    return retcode

@app.task
def compress_htr_data(filename_in):
    """ Run compress HTR data pipeline """
    img = 'convert_htr_data/convert_htr.simg'
    img = os.path.join(config.SINULARITY_APP_DIR, img)
    args_str = '{filename} -qdD'.format(filename=filename_in)
    retcode = singularity_run(args_str, img=img)
    return retcode  

@app.task
def run_sum_fil_8b(filename_in, ext_out='8b.fil', delete_orig=False, overwrite=False):
    """ Convert 32-bit filterbank to 8-bit 
    
    Args:
        filename_in (str): Path to filterbank file
        ext_out (str): Extension for output file. Default .8b.fil
        delete_orig (bool): Delete original file after conversion (default False)
        overwrite (bool): Overwrite existing output file, if it exists (default False)
    """
    img = 'sum_fil_8b/sum_fil_8b.simg'
    img = os.path.join(config.SINULARITY_APP_DIR, img)
    args_str = '{filename} -e {ext}'.format(filename=filename_in, ext=ext_out)
    if delete_orig:
        args_str += ' -d'
    if overwrite:
        args_str += ' -O'
    retcode = singularity_run(args_str, img=img)
    return retcode




if __name__ == "__main__":
    print("HI")
    #d = dispatch_to_node(compress_htr_data, 'blc01', args=['filename_test'])
    
    #print("Waiting for task to complete...")
    #while d.status == 'PENDING':
    #   time.sleep(0.5) 
    #print(d.result)
    # d = gather_filelists('/datax/PKSMB/GUPPI', '0002.fil')
    # test_singularity_all_nodes(d)

