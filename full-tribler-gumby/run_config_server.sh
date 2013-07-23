#!/bin/bash

PEERCOUNT=$1

rm -f ./output/config_server.log
echo "$0: Starting config server..." >> ./output/config_server.log
python -u gumby/scripts/config_server.py $PEERCOUNT 5 >>./output/config_server.log 2>&1
