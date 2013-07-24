#!/bin/bash

PEERCOUNT=$1

echo "$0: Starting config server..."

# wait for tracker

# create community

# start config server
# TODO: User logger.conf.cfgsrv in config_server.py
# TODO: Better way to run config_serverZ
export PYTHONPATH=gumby/scripts
python -c "from config_server import main; main()" $PEERCOUNT 5 > ./output/config_server.log 2>&1
