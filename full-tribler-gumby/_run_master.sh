#!/bin/bash

PEERCOUNT=$1

echo "run_master.sh: Starting config server..." > ./output/master.log
gumby/scripts/config_server.py $PEERCOUNT 120 2>&1 >> ./output/master.log
