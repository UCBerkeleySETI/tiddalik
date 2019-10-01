#!/usr/bin/env bash
PEASOUP_DIR=/home/dancpr/install/peasoup
DEDISP_DIR=/home/dancpr/install/dedisp

#PEASOUP_DIR=/datax2/users/dancpr/peasoup
#DEDISP_DIR=/datax2/users/dancpr/dedisp

export PATH=$PEASOUP_DIR/bin
export LD_LIBRARY_PATH=$DEDISP_DIR/lib
export LD_LIBRARY_PATH=/usr/local/cuda-8.0/lib64/:$LD_LIBRARY_PATH

echo $LD_LIBRARY_PATH

echo --- peasoup -v -p -i $1  --dm_start 0 --dm_end 500 -o $2  -k $3 -z $4 ---
peasoup -v -p -i $1  --dm_start 0 --dm_end 500 -o $2  -k $3 -z $4
