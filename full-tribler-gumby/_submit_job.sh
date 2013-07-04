#!/bin/bash

PEERCOUNT=$1

export PYTHONPATH=$PYTHONPATH:`pwd`/gumby

module load prun

# For TriblerNoGui:
export UNIQUE=`date +%s | sha256sum | base64 | head -c 32`
export TRIBLERPATH="tribler" # relative to user's home

prun node.sh $PEERCOUNT
