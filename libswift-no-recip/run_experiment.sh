#!/bin/bash

# configuration variables
[ -z $TIME ] && TIME=30
[ -z $SWIFT ] && SWIFT=./swift
[ -z $FILE_SIZE ] && FILE_SIZE=50 # in MiB

# constants
TMP_DIR=./tmp
DATE=$(date +'%F-%H-%M')
LOGS_DIR=./logs/$DATE
PLOTS_DIR=./plots/$DATE
PLOTS_LAST_DIR=./plots/last

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

trap 'kill $(jobs -p) || true; rm -rf $TMP_DIR' EXIT

# create directories
rm -rf $TMP_DIR || true
mkdir -p $TMP_DIR $LOGS_DIR $PLOTS_DIR $PLOTS_LAST_DIR || true

# generate_file <size_in_mib> <name>
function generate_file {
    mkdir -p $TMP_DIR/files
    dd if=/dev/urandom of=$TMP_DIR/files/$2 bs=$((1024*1024)) count=$1
    # TODO: save generated files
}

# prepare_seeder_files <name>
function prepare_seeder_files {
    local STORE=$TMP_DIR/peers/$1
    mkdir -p $STORE

    if [ ! -f $TMP_DIR/files/${1}.file ]; then
        generate_file $FILE_SIZE ${1}.file
    fi
    if [ ! -f $TMP_DIR/files/${1}.file.mhash ]; then
        $SWIFT -f $TMP_DIR/files/${1}.file -m -z 1024 --debug
    fi
    HASHES[$1]=`cat $TMP_DIR/files/${1}.file.mbinmap | head -2 | tail -1 | cut -d " " -f 3`

    # copy to seeder storage
    cp -f $TMP_DIR/files/${1}.file $STORE/${HASHES[$1]}
    cp -f $TMP_DIR/files/${1}.file.mhash $STORE/${HASHES[$1]}.mhash
    cp -f $TMP_DIR/files/${1}.file.mbinmap $STORE/${HASHES[$1]}.mbinmap

    echo "Prepared file with hash ${HASHES[$1]} for peer \"$1\""
}

# start_seeder <name>
function start_seeder {
    local STORE=$TMP_DIR/peers/$1
    local HASH=${HASHES[$1]}

    mkdir -p $LOGS_DIR/$1
    echo "Starting peer $1 (seeder)"
    ls -alh $STORE
    $DIR/process_guard.py -c "taskset -c 0 $SWIFT -e $STORE -l 1337 -c 10000 -z 1024 --progress --debug" -t $TIME -m $LOGS_DIR/$1 -o $LOGS_DIR/$1 &
    PIDS[$1]=$!
}

# start_leecher <name> <hash>
function start_leecher {
    local STORE=$TMP_DIR/peers/$1
    
    mkdir -p $STORE
    mkdir -p $LOGS_DIR/$1
    echo "Starting peer $1 (leecher) for hash $2"
    ls -alh $STORE
    sleep 1s
    $DIR/process_guard.py -c "taskset -c 1 $SWIFT -o $STORE -h $2 -t 127.0.0.1:1337 -z 1024 --progress" -t $(($TIME-1)) -m $LOGS_DIR/$1 -o $LOGS_DIR/$1 &
    PIDS[$1]=$!
}

echo "Experiment time: $TIME"

prepare_seeder_files src
start_seeder src
sleep 5s
start_leecher dst ${HASHES[src]}

wait ${PIDS[dst]}
wait ${PIDS[src]}

$DIR/parse_logs.py $LOGS_DIR/src
$DIR/parse_logs.py $LOGS_DIR/dst

gnuplot -e "logdir='$LOGS_DIR/src';peername='src';plotsdir='$PLOTS_DIR'" $DIR/resource_usage.gnuplot
gnuplot -e "logdir='$LOGS_DIR/dst';peername='dst';plotsdir='$PLOTS_DIR'" $DIR/resource_usage.gnuplot

gnuplot -e "logdir='$LOGS_DIR';plotsdir='$PLOTS_DIR'" $DIR/speed.gnuplot

rm $PLOTS_LAST_DIR/*
cp $PLOTS_DIR/* $PLOTS_LAST_DIR/
