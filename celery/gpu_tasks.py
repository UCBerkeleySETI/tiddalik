"""
# gpu_tasks.py

Tiddalik tasks for celery 
"""

import time
import os
import glob

import config
from config import app, gpu_app
from singularity import singularity_exec, singularity_run
from tasks import dispatch_to_node_priority, gather_filelists

def dispatch_to_node(taskfn, node_id, args=None, kwargs=None):
    """ Run a task on a given node via celery

    Args:
        taskfn (app.task): A function decorated with celery's @app.task
        node_id (str): Hostname on which to run the task
        args (list): List of arguments to pass to the taskfn
    """
    queue_id = '{node}_gpu'.format(node=node_id)
    routing_key = '{q}.run'.format(q=queue_id)
    d = taskfn.apply_async(args=args, kwargs=kwargs, queue=queue_id, routing_key=routing_key)
    return d

@gpu_app.task
def run_heimdall(filename_in):
    """ Run heimdall on data """
    img = '/home/obs/tiddalik/celery/apps/heimdall/heimdall.simg'
    #args_str = '{filename} -qdD'.format(filename=filename_in)
    args_str = '-h'
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

