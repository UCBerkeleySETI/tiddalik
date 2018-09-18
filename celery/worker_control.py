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
    """ Stop roachnest and jupyter servers """
    with warn_only():
        run("tmux kill-session -t tiddalik")

@task
@parallel
@hosts(config.nodes)
def start_worker():
	""" Start roachnest web gui and jupyter servers """
	with warn_only():
		venv  = config.VIRTUALENV
		tdir = config.RUN_DIR
		#run("source {env} cd {tdir}; tmux new -d -s tiddalik './start_worker.py'".format(env=env, tdir=tdir))
		run("{venv}; cd {tdir}; tmux new -d -s tiddalik 'python start_worker.py'".format(venv=venv, tdir=tdir))

def start_workers():
    execute(start_worker)

def stop_workers():
    execute(stop_worker)

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
        print("%24s: %48s" % (key, desc))

cmds = {
    'start_workers': ['Start worker processes on compute nodes', start_workers],
    'stop_workers': ['Stop all workers on compute nodes', stop_workers],
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



