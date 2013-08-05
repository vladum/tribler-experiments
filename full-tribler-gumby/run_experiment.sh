#!/bin/bash

# Usage: ./run_experiment.sh <your_das4_username> <peercount>

# We need to generate a workspace directory for gumby with the proper scripts,
# configuration file, and gumby itself. Next, we let gumby do his thing. Edit
# your gumby configuration here.

# Script arguments.
DAS4USER=$1
PEERCOUNT=$2

# Experiment name.
EXPERIMENT_NAME="FullTriblerNoGui"
EXPERIMENT_DIR="`pwd`/$EXPERIMENT_NAME"

# Create gumby experiment directory.
mkdir -p $EXPERIMENT_DIR 2>/dev/null
rsync -avz --delete --exclude "$(basename $EXPERIMENT_DIR)" \
	--exclude "$(basename $0)" --exclude "\.*" ./ $EXPERIMENT_DIR

# Generate gumby configuration file.
cat > $EXPERIMENT_DIR/$EXPERIMENT_NAME.config << CONFIGFILE
virtualenv_dir = "/home/$DAS4USER/venv"
workspace_dir = "$EXPERIMENT_DIR"
#head_nodes = "$DAS4USER@fs3.das4.tudelft.nl",
head_nodes = "$DAS4USER@fs0.das4.cs.vu.nl",

tracker_cmd = "./run_tracker.sh"
config_server_cmd = "./run_config_server.sh $PEERCOUNT"

# Tracker running on the first head node.
tracker_run_remote = True
tracker_port = 7788

remote_setup_cmd = "das4_setup.sh" # installs libraries and stuff on DAS4
remote_instance_cmd = "./submit_job.sh $PEERCOUNT" # submit actual job to DAS4

scenario_file = "scenario" # relative to PROJECTROOT
CONFIGFILE

# Start gumby.
python gumby/run.py $EXPERIMENT_DIR/$EXPERIMENT_NAME.config
