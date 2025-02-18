"""
# tasks.py

Tiddalik tasks for celery 
"""

import time
import os
import glob
import fnmatch

import config
from config import app
from singularity import singularity_exec, singularity_run
import socket

def dispatch_to_node(taskfn, node_id, args=None, kwargs=None):
    """ Run a task on a given node via celery

    Args:
        taskfn (app.task): A function decorated with celery's @app.task
        node_id (str): Hostname on which to run the task
        args (list): List of arguments to pass to the taskfn
    """
    d = taskfn.apply_async(args=args, kwargs=kwargs, queue=node_id, routing_key='{node_id}.run'.format(node_id=node_id))
    return d

def dispatch_to_node_single_cpu(taskfn, node_id, args=None, kwargs=None):
    """ Run a task on a given node via celery -- to priority worker

    Args:
        taskfn (app.task): A function decorated with celery's @app.task
        node_id (str): Hostname on which to run the task
        args (list): List of arguments to pass to the taskfn
    """
    q = '{n}_single_cpu'.format(n=node_id)
    rk = '{q}.run'.format(q=q)
    d = taskfn.apply_async(args=args, kwargs=kwargs, queue=q, routing_key=rk)
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

def gather_filelists_recursive(path_to_files, file_ext, timeout=60):
    """ Gather filelists from all nodes

    Uses get_filelist task.
    """
    dd = {}
    for node in config.nodes:
        dd[node] = dispatch_to_node_priority(get_filelist_recursive, node, args=(path_to_files, file_ext))
    
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
def get_filelist_recursive(path_to_files, file_ext):
    """ Generate a list of files on which to run -- recursive """
    matches = []
    for root, dirnames, filenames in os.walk(path_to_files):
        for filename in fnmatch.filter(filenames, '*.{ext}'.format(ext=file_ext)):
                matches.append(os.path.join(root, filename))
    return matches

def rsync_file_to_host(filename, dest_host, dest_path, prepend_hostname=True):
    """ Upload a file to blpd0 using rsync """
    if prepend_hostname:
        host = socket.gethostname()
        dn = os.path.dirname(filename)
        bn = os.path.basename(filename)
        filename_out = '{host}_{fn}'.format(host=host, fn=bn)
    else:
        filename_out = filename
    filepath_out = os.path.join(dest_path, filename_out).strip('/')

    cmd = 'rsync -av --progress {fn} rsync://{host}/{path}'.format(fn=filename, host=dest_host, path=filepath_out)
    print(cmd)
    retcode = os.system(cmd)
    return retcode

@app.task
def rsync_file(filename, dest_host, dest_path, prepend_hostname=True):
    """ Upload a file to blpd0 using rsync """
    return rsync_file_to_host(filename, dest_host, dest_path, prepend_hostname) 


def file_rsync_blpd0(filename, prepend_hostname=True):
    """ Upload a file to blpd0 using rsync """
    if prepend_hostname:
        host = socket.gethostname()
        dn = os.path.dirname(filename)
        bn = os.path.basename(filename)
        filename_out = '{host}_{fn}'.format(host=host, fn=bn)
    else:
        filename_out = filename
    print('rsync -av --progress {fn} rsync://blpd0.ssl.berkeley.edu/datax2/{fn_out}'.format(fn=filename, fn_out=filename_out))
    retcode = os.system('rsync -av --progress {fn} rsync://blpd0.ssl.berkeley.edu/datax2/{fn_out}'.format(fn=filename, fn_out=filename_out))
    return retcode

@app.task
def upload_to_blpd0(filename, prepend_hostname=True, delete=False):
    """ Upload a file to blpd0 using rsync """
    print "Uploading %s" % filename
    ret = file_rsync_blpd0(filename, prepend_hostname=True) 
    is_deleted = False
    if delete is True and ret == 0:
        try:
            os.remove(filename)
            is_deleted=True
        except:
            print "Couldn't delete %s" % filename
            pass
    return (ret, is_deleted)

@app.task
def run_2b_extract(filename_in, f0=1420.5, upload=True, delete_after_upload=True):
    """ Run SETI@HOME 2-bit extraction code """
    img = 'setiathome/setiathome.simg'
    img = os.path.join(config.SINGULARITY_APP_DIR, img)
    fout = os.path.splitext(filename_in)[0] + 'f{f0}.raw2b'.format(f0=f0)
    args_str = '{filename} {f0} {fout}'.format(filename=filename_in, f0=f0, fout=fout)
    retcode = singularity_run(args_str, img=img)
    
    is_deleted = False
    retcode_up = -1
    if retcode == 0 and upload is True:
        retcode_up = file_rsync_blpd0(fout, prepend_hostname=True)
    if retcode == 0 and retcode_up == 0 and delete_after_upload is True:
        try:
            os.remove(fout)
            is_deleted = True
        except:
            is_deleted = False
    return (retcode, retcode_up, is_deleted)

@app.task
def run_extract_21cm(filename_in):
    """ Extract 21-cm line from multibeam hires file """
    pyscript = os.path.join(config.SINGULARITY_APP_DIR, 'extract_21cm/extract_21cm.py')
    retcode = os.system('python {py} {fn}'.format(py=pyscript, fn=filename_in))
    return retcode

@app.task
def compress_htr_data(filename_in):
    """ Run compress HTR data pipeline """
    img = 'convert_htr_data/convert_htr.simg'
    img = os.path.join(config.SINGULARITY_APP_DIR, img)
    args_str = '{filename} -qdD'.format(filename=filename_in)
    retcode = singularity_run(args_str, img=img)
    return retcode  

@app.task
def run_turboseti(filename_in, outdir):
    """ Run turboseti on data """
    img = 'turboseti/turboseti.simg'
    img = os.path.join(config.SINGULARITY_APP_DIR, img)
    args_str = '{fn} -o {outdir}'.format(fn=filename_in, outdir=outdir)
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
    img = os.path.join(config.SINGULARITY_APP_DIR, img)
    args_str = '{filename} -e {ext}'.format(filename=filename_in, ext=ext_out)
    if delete_orig:
        args_str += ' -d'
    if overwrite:
        args_str += ' -O'
    retcode = singularity_run(args_str, img=img)
    return retcode

@app.task
def safe_delete_post_turboseti(filename_in):
    """ Delete 0000.fil file iff 0000.h5 exists and turboseti has run 
    
    Args: filename_in (str): Name of 0000.fil file to check

    Notes: checkes for .h5, .dat and .turboseti.complete
    """
    fbase = os.path.splitext(filename_in)[0]
    fn_h5 = fbase + '.h5'
    fn_dat = fbase + '.dat'
    fn_comp = fbase + '.turboseti.complete'
    exists = os.path.exists
    if exists(fn_h5) and  exists(fn_dat) and exists(fn_comp):
        h5_size = os.path.getsize(fn_h5)
        fil_size = os.path.getsize(filename_in)
        if h5_size * 2.0 > fil_size:
            print("ALL OK: %s" % filename_in)
            os.remove(filename_in)
            return("ALL OK: %s" % filename_in)
        else:
            print("FSIZE NOT OK: %s" % filename_in)
            return("FSIZE NOT OK: %s" % filename_in)
    else:
        print("NOT OK: %s" % filename_in)
        return("NOT OK: %s" % filename_in)

@app.task
def run_tommy_pipe_rfifind(filename_in):
    """ Run turboseti on data """
    img = 'tommy_pipe/tommy_pipe.simg'
    img = os.path.join(config.SINGULARITY_APP_DIR, img)
    args_str = '{fn}'.format(fn=filename_in)
    retcode = singularity_run(args_str, img=img, app='rfifind')
    return retcode  

@app.task
def run_tommy_pipe_prepfold(filename_in):
    """ Run turboseti on data """
    img = 'tommy_pipe/tommy_pipe.simg'
    img = os.path.join(config.SINGULARITY_APP_DIR, img)
    args_str = '{fn}'.format(fn=filename_in)
    retcode = singularity_run(args_str, img=img, app='prepfold')
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

