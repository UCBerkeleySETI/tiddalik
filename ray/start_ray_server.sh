ray start --head --redis-port=6380

pssh -h workers.txt -I < start_ray_worker.sh
