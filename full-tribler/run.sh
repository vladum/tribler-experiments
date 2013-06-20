#!/bin/bash

module load prun

source $HOME/my-python/bin/activate

prun -o peer node.py 4
