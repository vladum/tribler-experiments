#!/bin/bash

PEERCOUNT=$1

echo "Starting config server..." > ./output/master.log
python gumby/scripts/config_server.py $PEERCOUNT 10 2>&1 >> ./output/master.log
