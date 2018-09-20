#!/usr/bin/env python
"""
# start_worker.py
Start a tiddalik worker (using celery) on a host
"""

import os
import socket
import config
from datetime import datetime

if __name__ == "__main__":

    import argparse
    p = argparse.ArgumentParser('Start a tiddalik/celery worker process')
    p.add_argument('-c', '--cores', help='Number of cores', type=int, default=1)
    args = p.parse_args()
    
    ncores = args.cores
    host = socket.gethostname()
    dt = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    logname = '{host}_gpu_{dt}.log'.format(host=host, dt=dt)
    logfile = os.path.join(config.LOG_PATH, logname)

    cstr = 'celery -A gpu_tasks worker -n {host}_gpu_worker -c {ncores} -Q {host}_gpu -E -l INFO -f {logfile}'.format(host=host, ncores=ncores, logfile=logfile)
    print(cstr)
    os.system(cstr)

