#!/bin/bash

export LD_PRELOAD=/home/vdumitre/venv/m2cdeps/lib/libcrypto.so.10

# for libswift
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/vdumitre/libs/lib

python -u node.py $@
