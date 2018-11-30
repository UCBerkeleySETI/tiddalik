# ray.py at Parkes

Ray is a flexible, high-performance distributed execution framework. 

## Starting and stopping

TO start at Parkes, run as obs@bl_head:

```
> ./start_ray_server.sh
```

To stop, run 

```
> ./stop_ray_server.sh
```

## Juptyer notebooks

To use ray, you need to setup a jupyter notebook. To check if one is 
running, run `tmux ls` and look for a session called jupyter.

If there is no jupyter server running, you can start one as follows:

```
> tmux new -s jupyter
> cd /home/obs; jupyter lab --no-browser --port=10000
(Ctrl + B, D to detach)
```

Then make an ssh tunnel on your laptop/desktop over to bl-head
to forward the port:

```
ssh -L 10000:localhost:10000 pks-blh
```

(Assuming you have setup your tunnels in `.ssh/config`). 

Finally, open your browser and browser to [http://localhost:10000].
