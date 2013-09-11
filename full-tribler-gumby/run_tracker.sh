#!/bin/bash

TRIBLERPATH="$HOME/tribler" # relative to user's home

# Start Dispersy tracker.
mkdir -p tmp/tracker tmp/tracker/sqlite
pushd .
cd tmp/tracker
# no default bootstrap nodes
echo "$(host $HOSTNAME | cut -d " " -f 4) 31337" > bootstraptribler.txt
LOGGER_CONF=$PROJECTROOT/logger.conf.tracker PYTHONPATH=$PYTHONPATH:$TRIBLERPATH python $PROJECTROOT/util/run_tracker.py --ip 0.0.0.0 --port 31337 &
TRACKER_PID=$!
popd

# wait for tracker to start, then create the community
echo "Creating BarterCommunity"
mkdir -p tmp/creator tmp/creator/sqlite
pushd .
cd tmp/creator
LOGGER_CONF=$PROJECTROOT/logger.conf.tracker PYTHONPATH=$PYTHONPATH:$TRIBLERPATH python $PROJECTROOT/util/create_bc3_community.py --tracker-ip 127.0.0.1 --tracker-port 31337
popd

echo "BarterCommunity master member: $(cat $PROJECTROOT/tmp/bc3_master)"

wait $TRACKER_PID
