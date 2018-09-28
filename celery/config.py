""" 
# config.py

Configuration for tiddalik application (using Python Celery)
"""

from celery import Celery
from kombu import Queue, Exchange

redis_db = 'redis://130.155.181.233:6379/1'
nodes = ['blc{i}{j}'.format(i=ii, j=jj) for ii in range(0, 3) for jj in range(0, 8)]
nodes += ['blc30', 'blc31', 'blc32']

# Singularity runtime settings
SINGULARITY_EXE = '/usr/local/singularity/bin/singularity'
SINGULARITY_IMG = '/opt/singularity/psrkit.simg'
SINGULARITY_FLAGS = '--bind /datax,/datax2 --nv'

# Tiddalik directory
RUN_DIR  = '/home/obs/tiddalik/celery'
VIRTUALENV = 'source /opt/pyve/activate obs' 

# Logfile path
SINGULARITY_APP_DIR = '/home/obs/tiddalik/celery/apps/'
LOG_PATH = '/home/obs/logs/tiddalik'


# Setup a bunch of routes and queues for each node
app_queues = []
app_routes = {}

for node in nodes:
    q = Queue(node, Exchange(node), routing_key='{node}.#'.format(node=node))
    r = {'queue': node, 'routing_key': '{node}.#'.format(node=node)}

    app_queues.append(q)
    app_routes[node] = r

    pn = '{node}_priority'
    pq = Queue(pn, Exchange(pn), routing_key='{node}.#'.format(node=pn))
    pr = {'queue': pn, 'routing_key': '{node}.#'.format(node=pn)}

    app_queues.append(pq)
    app_routes[pn] = pr

    pn = '{node}_single_cpu'
    pq = Queue(pn, Exchange(pn), routing_key='{node}.#'.format(node=pn))
    pr = {'queue': pn, 'routing_key': '{node}.#'.format(node=pn)}

    app_queues.append(pq)
    app_routes[pn] = pr




app = Celery('tasks',
             backend=redis_db, 
             broker=redis_db
             )

app.conf.task_queues = app_queues
app.conf.task_routes = app_routes


# Setup app for GPU tasks too
gpu_app_queues = []
gpu_app_routes = {}

for node in nodes:
    node_gpu = '{node}_gpu'.format(node=node)
    q = Queue(node_gpu, Exchange(node_gpu), routing_key='{node_gpu}.#'.format(node_gpu=node_gpu))
    r = {'queue': node_gpu, 'routing_key': '{node_gpu}.#'.format(node_gpu=node_gpu)}
    
    gpu_app_queues.append(q)
    gpu_app_routes[node_gpu] = r

gpu_app = Celery('gpu_tasks',
             backend=redis_db, 
             broker=redis_db
             )

gpu_app.conf.task_queues = gpu_app_queues
gpu_app.conf.task_routes = gpu_app_routes


