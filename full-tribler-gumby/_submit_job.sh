#!/bin/bash

PEERCOUNT=$1

export PYTHONPATH=$PYTHONPATH:`pwd`/gumby

module load prun

prun node.py $PEERCOUNT 2>&1 > ./output/job.log
