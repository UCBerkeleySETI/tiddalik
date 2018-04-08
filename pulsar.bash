#!/bin/bash
# Set environment variables for pulsar software, bash version
echo "Setting pulsar64 environment..."

# Not installed yet
#export HEADAS=/home/pulsar64/src/heasoft-6.6.2/x86_64-unknown-linux-gnu-libc2.3.4
#alias ftools=". $HEADAS/headas-init.sh"

# Note, this is now for pulsar analysis type stuff only, NOT guppi control:
PSR64=/usr/local/pulsar64
PYTHONBASE=/usr
PYTHONVER=2.7
export PSRCAT_FILE=$PSR64/share/psrcat.db
export PGPLOT_DIR=/usr/lib/pgplot5
export PRESTO=$PSR64/src/presto
export TEMPO=$PSR64/src/tempo
export TEMPO2=$PSR64/share/tempo2
export PATH=$PSR64/bin:$PRESTO/bin:$PYTHONBASE/bin:$PATH
# /opt thing is automatic?
export PYTHONPATH=$PSR64/lib/python$PYTHONVER/site-packages:$PRESTO/lib/python:$PYTHONBASE/lib/python$PYTHONVER:$PYTHONBASE/lib/python$PYTHONVER/site-packages
export LD_LIBRARY_PATH=$PSR64/lib:$PRESTO/lib:$TEMPO2/lib:$PYTHONBASE/lib:/usr/lib/x86_64-linux-gnu
export LIBRARY_PATH=$PSR64/lib:$PRESTO/lib:$TEMPO2/lib:$PYTHONBASE/lib:/usr/lib/x86_64-linux-gnu
export CPATH=/usr/local/include
