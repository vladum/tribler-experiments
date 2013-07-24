#!/bin/bash

TRIBLERPATH="$HOME/tribler" # relative to user's home

# Start Dispersy tracker.
mkdir -p tmp/tracker
pushd .
cd tmp/tracker
cp $PROJECTROOT/logger.conf.tracker ./logger.conf # default logger.conf
LOGGER_CONF=$PROJECTROOT/logger.conf.tracker python $PROJECTROOT/util/run_tracker.py --tribler $TRIBLERPATH --ip 0.0.0.0 --port 31337
popd
