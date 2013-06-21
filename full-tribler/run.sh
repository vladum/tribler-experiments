#!/bin/bash

module load prun

source $HOME/my-python/bin/activate

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/libs/lib:$HOME/libs/lib64
export TRIBLERPATH=../../tribler

UNIQUE=`date +%s | sha256sum | base64 | head -c 32`

echo "UNIQUE is: $UNIQUE"

prun -v -o peer node.py 4 $UNIQUE | tee hosts

echo "Done."
HOSTS=`cat hosts | head -1`
echo $HOSTS
