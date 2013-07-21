#!/bin/bash

TRIBLERPATH="$HOME/tribler" # relative to user's home

# Start Dispersy tracker.
mkdir -p tracker
cp logger.conf.tracker ./tracker/logger.conf
pushd .
cd tracker
python $PROJECTROOT/util/run_tracker.py --tribler $TRIBLERPATH --ip 0.0.0.0 --port 31337
popd
