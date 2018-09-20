# Singularity container psrkit

A pulsar-related singularity container

## Build from Recipe

From the headnode (does not work from compute nodes)

sudo /usr/local/singularity/bin/singularity build psrkit.simg Recipe

(You need to be sudo user)

## Run code with GPU

singularity shell --nv psrkit.simg

## Bind dirs

singularity shell --bind /datax,/datax2 --nv psrkit.simg

