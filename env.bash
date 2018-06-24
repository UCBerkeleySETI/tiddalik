
# IPYTHON
export IPYTHONDIR=/tmp/pri229

# bifrost
export LD_LIBRARY_PATH=/usr/local/lib

# CUDA
export CUDA_ROOT="/usr/local/cuda-8.0"
export CUDA_INC_DIR="/usr/local/cuda-8.0/include"

# HDF5
export PATH="/usr/local/hdf5/bin:$PATH"
export LD_LIBRARY_PATH="/usr/local/hdf5/lib:$LD_LIBRARY_PATH"
export HDF5_PLUGIN_PATH="/usr/local/hdf5/lib/plugin"
export CPATH="/usr/local/hdf5/include:$CPATH"
export HDF5_DIR="/usr/local/hdf5"
export LIBRARY_PATH="/usr/local/hdf5/lib:$LIBRARY_PATH"

# BIFROST
export LD_LIBRARY_PATH="/usr/local/cuda-8.0/lib64:/usr/local/lib:$LD_LIBRARY_PATH"
export PATH=/usr/local/cuda-8.0/bin:$PATH
export BIFROST_INCLUDE_PATH=/usr/local/include/bifrost

# GCC 5.4
export LD_LIBRARY_PATH=/usr/local/gcc-5.4/lib64/:$LD_LIBRARY_PATH
export LIBRARY_PATH=/usr/local/gcc-5.4/lib64:$LIBRARY_PATH
export PATH=/usr/local/gcc-5.4/bin:$PATH


# PYTHON VIRTUALENV
. /opt/pyve/activate obs

# ALIAS 4 PULSRZ
export pulsar_me='source /usr/local/pulsar64/pulsar.bash'

#sigpyproc hack
export LD_LIBRARY_PATH=/home/pri229/install/sigpyproc/lib/c/:$LD_LIBRARY_PATH

echo "Setting DCPY / HDF5 env..."
