#!/bin/bash

PEERCOUNT=$1

rm -f ./output/master.log
echo "run_master.sh: Starting config server..." >> ./output/master.log
python -u gumby/scripts/config_server.py $PEERCOUNT 5 >>./output/master.log 2>&1
