#!/bin/bash

# Usage: ./run_experiment.sh <your_das4_username> <peercount>

# We need to generate a workspace directory for gumby with the proper scripts,
# configuration file, and gumby itself. Next, we let gumby do his thing.

DAS4USER=$1
PEERCOUNT=$2

EXPERIMENT_NAME="FullTriblerNoGui"
EXPERIMENT_DIR="`pwd`/FullTriblerNoGui"

mkdir ./$EXPERIMENT_NAME 2>/dev/null

# Dispersy tracker that will be run on the head node
cp ./_run_tracker.sh ./$EXPERIMENT_NAME/run_tracker.sh 2>/dev/null

# The experiment master. Will also run on the head node. For this experiment
# this is just the config server.
cp ./_run_master.sh ./$EXPERIMENT_NAME/run_master.sh 2>/dev/null

# The actual job submission script that will reserve and run instances on DAS4.
cp ./_submit_job.sh ./$EXPERIMENT_NAME/submit_job.sh 2>/dev/null

# Copy the whole gumby to the workspace
cp -R ./gumby ./$EXPERIMENT_NAME/ 2>/dev/null

# Code that will be run on the DAS4 nodes
cp ./node.py ./$EXPERIMENT_NAME/node.py 2>/dev/null

cat > ./$EXPERIMENT_NAME/$EXPERIMENT_NAME.config << CONFIGFILE
workspace_dir = "$EXPERIMENT_DIR"
head_nodes = "$DAS4USER@fs3.das4.tudelft.nl",

tracker_cmd = "./run_tracker.sh"
config_server_cmd = "./run_master.sh $PEERCOUNT"

# Tracker running on the first head node.
tracker_run_remote = True
tracker_port = 7788

local_setup_cmd = ":" # no local setup needed
remote_setup_cmd = "das4_setup.sh" # installs libraries and stuff on DAS4

local_instance_cmd = ":" # no local instance
remote_instance_cmd = "./submit_job.sh $PEERCOUNT" # submit actual job to DAS4

use_local_venv = False # doesn't matter, nothing is run locally
use_local_systemtap = False # doesn't matter, nothing is run locally
CONFIGFILE

python gumby/run.py ./$EXPERIMENT_NAME/$EXPERIMENT_NAME.config
