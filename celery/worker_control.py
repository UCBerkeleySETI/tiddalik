#!/usr/bin/env python
"""
# dispatch_tasks.py

Dispatch and manage tasks to the tiddalik worker nodes
"""

from fabric.api import *
import config
from config import app

def purge_all_pending():
    """ Purge all pending tasks in celery queue """
    app.control.purge()

@task
@parallel
@hosts(config.nodes)
def stop_worker():
    """ Stop tiddalik worker """
    with warn_only():
        run("tmux kill-session -t tiddalik")


@task
@parallel
@hosts(config.nodes)
def stop_gpu_worker():
    """ Stop tiddalik GPU worker """
    with warn_only():
        run("tmux kill-session -t tiddalik_gpu")

@task
@parallel
@hosts(config.nodes)
def stop_priority_worker():
    """ Stop tiddalik priority worker """
    with warn_only():
        run("tmux kill-session -t tiddalik_priority")

@task
@parallel
@hosts(config.nodes)
def start_worker():
	""" Start tiddalik worker """
	with warn_only():
		venv  = config.VIRTUALENV
		tdir = config.RUN_DIR
		run("{venv}; cd {tdir}; tmux new -d -s tiddalik 'python start_worker.py'".format(venv=venv, tdir=tdir))

@task
@parallel
@hosts(config.nodes)
def start_gpu_worker():
	""" Start tiddalik GPU worker """
	with warn_only():
		venv  = config.VIRTUALENV
		tdir = config.RUN_DIR
		run("{venv}; cd {tdir}; tmux new -d -s tiddalik_gpu 'python start_worker_gpu.py'".format(venv=venv, tdir=tdir))

@task
@parallel
@hosts(config.nodes)
def start_priority_worker():
	""" Start tiddalik priority worker """
	with warn_only():
		venv  = config.VIRTUALENV
		tdir = config.RUN_DIR
		run("{venv}; cd {tdir}; tmux new -d -s tiddalik_priority 'python start_worker_priority.py'".format(venv=venv, tdir=tdir))

def start_workers():
    execute(start_worker)

def stop_workers():
    execute(stop_worker)

def start_gpu_workers():
    execute(start_gpu_worker)

def stop_gpu_workers():
    execute(stop_gpu_worker)

def start_priority_workers():
    execute(start_priority_worker)

def stop_priority_workers():
    execute(stop_priority_worker)

def start_all_workers():
    execute(start_worker)
    execute(start_priority_worker)
    execute(start_gpu_worker)

def stop_all_workers():
    execute(stop_worker)
    execute(stop_gpu_worker)
    execute(stop_priority_worker)

def print_header():
    hdr = """
      _______ _     _     _       _ _ _    
     |__   __(_)   | |   | |     | (_) |   
        | |   _  __| | __| | __ _| |_| | __
        | |  | |/ _` |/ _` |/ _` | | | |/ /
        | |  | | (_| | (_| | (_| | | |   < 
        |_|  |_|\__,_|\__,_|\__,_|_|_|_|\_\\

    --- Breakthrough Listen process manager ---
                                            """
                                       
    print(hdr) 

def list_cmds():
    print_header()
    print("Available commands:")
    keys = sorted(cmds.keys())
    for key in keys:
        desc, cmd_fn = cmds[key]
        print("%24s: %54s" % (key, desc))

cmds = {
    'start_cpu_workers': ['Start worker processes on compute nodes', start_workers],
    'start_all_workers': ['Start *all* worker processes on compute nodes', start_all_workers],
    'start_gpu_workers': ['Start GPU worker process (1 core) on compute nodes', start_gpu_workers],
    'start_priority_workers': ['Start priority  worker process on compute nodes', start_priority_workers],
    'stop_cpu_workers': ['Stop workers on compute nodes', stop_workers],
    'stop_all_workers': ['Stop *all* workers on compute nodes', stop_all_workers],
    'stop_gpu_workers': ['Stop all GPU workers on compute nodes', stop_gpu_workers],
    'stop_priority_workers': ['Stop all priority workers on nodes', stop_priority_workers],
    'purge_all_pending': ['Purge all pending tasks in celery queue', purge_all_pending],
    
}

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description='Tiddalik control (via celery workload manager)')
    p.add_argument('cmd', help='Command to run', type=str, nargs='?')
    p.add_argument('-l', '--list', help='List commands', action='store_true', default=False)
    args = p.parse_args()

    if args.list or args.cmd is None:
        list_cmds()
        exit()
    if args.cmd in cmds:
        print("Running %s..." % args.cmd)
        cmds[args.cmd][1]()
    else:
        print("Error: could not find command %s" % args.cmd)
        list_cmds()
        exit()



