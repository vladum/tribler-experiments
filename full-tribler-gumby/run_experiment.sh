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
cp ./run_tracker.sh ./$EXPERIMENT_NAME/ 2>/dev/null

# Experiment config server to be run on the head node.
cp ./run_config_server.sh ./$EXPERIMENT_NAME/ 2>/dev/null

# The actual job submission script that will reserve and run instances on DAS4.
cp ./submit_job.sh ./$EXPERIMENT_NAME/ 2>/dev/null

# Copy the whole gumby to the workspace
cp -R ./gumby ./$EXPERIMENT_NAME/ 2>/dev/null

# Code that will be run on the DAS4 nodes
cp ./node.py ./$EXPERIMENT_NAME/node.py 2>/dev/null
cp ./node.sh ./$EXPERIMENT_NAME/node.sh 2>/dev/null
cp ./tribler_nogui.py ./$EXPERIMENT_NAME/tribler_nogui.py 2>/dev/null
cp ./logger.conf ./$EXPERIMENT_NAME/logger.conf 2>/dev/null
cp ./logger.conf.tracker ./$EXPERIMENT_NAME/logger.conf.tracker 2>/dev/null
cp ./scenario ./$EXPERIMENT_NAME/scenario 2>/dev/null
cp -R ./util ./$EXPERIMENT_NAME/util 2>/dev/null

cat > ./$EXPERIMENT_NAME/$EXPERIMENT_NAME.config << CONFIGFILE
virtualenv_dir = "/home/$DAS4USER/venv"
workspace_dir = "$EXPERIMENT_DIR"
head_nodes = "$DAS4USER@fs3.das4.tudelft.nl",

tracker_cmd = "./run_tracker.sh"
config_server_cmd = "./run_config_server.sh $PEERCOUNT"

# Tracker running on the first head node.
tracker_run_remote = True
tracker_port = 7788

remote_setup_cmd = "das4_setup.sh" # installs libraries and stuff on DAS4
remote_instance_cmd = "./submit_job.sh $PEERCOUNT" # submit actual job to DAS4

scenario_file = "scenario" # relative to PROJECTROOT
CONFIGFILE

python gumby/run.py ./$EXPERIMENT_NAME/$EXPERIMENT_NAME.config
