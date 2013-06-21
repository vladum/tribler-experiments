#!/bin/bash

module load prun

source $HOME/my-python/bin/activate

UNIQUE=`date +%s | sha256sum | base64 | head -c 32`
prun -o peer node.py 4 $UNIQUE
