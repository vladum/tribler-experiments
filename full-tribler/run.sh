#!/bin/bash

module load prun

source $HOME/my-python/bin/activate

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/libs/lib:$HOME/libs/lib64
export TRIBLERPATH=../../tribler

UNIQUE=`date +%s | sha256sum | base64 | head -c 32`
prun -o peer node.py 4 $UNIQUE
