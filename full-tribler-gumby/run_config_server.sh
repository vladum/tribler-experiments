#!/bin/bash

PEERCOUNT=$1

echo "$0: Starting config server... CWD: $PWD"

# wait for tracker

# create community

# start config server
# TODO: User logger.conf.cfgsrv in config_server.py
# TODO: Better way to run config_serverZ
export PYTHONPATH=gumby/scripts
python -u -c "from config_server import main; main()" $PEERCOUNT 5 1>./output/config_server.out 2>./output/config_server.err
