#!/bin/bash

PEERCOUNT=$1

module load prun

prun node.py $PEERCOUNT 2>&1 > ./output/job.log
