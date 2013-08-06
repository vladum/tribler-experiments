#!/bin/bash

# Usage: ./run_experiment.sh <your_das4_username> <das4_fs> <peercount>

# We need to generate a workspace directory for gumby with the proper scripts,
# configuration file, and gumby itself. Next, we let gumby do his thing. Edit
# your gumby configuration here.

# Script arguments.
DAS4USER=$1
DAS4FS=$2
PEERCOUNT=$3

: ${DAS4USER:?"Please give DAS4 username as the 1st argument."}
: ${DAS4FS:?"Please give DAS4 front server host as the 2nd argument."}
: ${PEERCOUNT:?"How many peers should I start? (3rd argument)"}

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
head_nodes = "$DAS4USER@$DAS4FS",

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
