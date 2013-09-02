#!/bin/bash

# configuration variables
[ -z $TIME ] && TIME=30
[ -z $SWIFT ] && SWIFT=./swift
[ -z $FILE_SIZE ] && FILE_SIZE=50 # in MiB
[ -z $DEBUG ] && DEBUG=false

# to run peers on separate cores (affinity) redef these (max 8)
# TODO: I know this is crappy.. .sorry
[ -z $AFNTY0 ] && AFNTY0=0
[ -z $AFNTY1 ] && AFNTY1=0
[ -z $AFNTY2 ] && AFNTY2=0
[ -z $AFNTY3 ] && AFNTY3=0
[ -z $AFNTY4 ] && AFNTY4=0
[ -z $AFNTY5 ] && AFNTY5=0
[ -z $AFNTY6 ] && AFNTY6=0
[ -z $AFNTY7 ] && AFNTY7=0
AFNTY=($AFNTY0 $AFNTY1 $AFNTY2 $AFNTY3 $AFNTY4 $AFNTY5 $AFNTY6 $AFNTY7)

# ------------------------------------------------------------------------------

echo "Affinity array: ${AFNTY[@]}"

# constants
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TMP_DIR=./tmp
DATE=$(date +'%F-%H-%M')
LOGS_DIR=./logs/$DATE
PLOTS_DIR=./plots/$DATE
PLOTS_LAST_DIR=./plots/last
PEERID=0
declare -A PIDS
declare -A UPRATE
declare -A DWRATE

trap 'kill $(jobs -p) || true; rm -rf $TMP_DIR; killall -9 swift' EXIT

# create directories
rm -rf $TMP_DIR || true
mkdir -p $TMP_DIR $LOGS_DIR $PLOTS_DIR $PLOTS_LAST_DIR || true

# ------------------------------------------------------------------------------

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

# start_seeder <name> <time>
function start_seeder {
    local STORE=$TMP_DIR/peers/$1
    local HASH=${HASHES[$1]}

    mkdir -p $LOGS_DIR/$1
    echo "Starting peer $1 (seeder)"
    ls -alh $STORE
    if $DEBUG; then
        DBGSTR="--debug"
    else
        DBGSTR=""
    fi
    # round robin affinity using the optionally supplied array
    local CPU=${AFNTY[$PEERID % ${#AFNTY[@]}]}
    local UPRATE=$(eval "echo \$UPRATE_$1")
    local DOWNRATE=$(eval "echo \$DOWNRATE_$1")
    $DIR/process_guard.py -c "taskset -c $CPU $SWIFT $UPRATE $DOWNRATE -e $STORE -l 1337 -c 10000 -z 1024 --progress $DBGSTR" -t $2 -m $LOGS_DIR/$1 -o $LOGS_DIR/$1 &
    PIDS[$1]=$!
    PEERID=$(($PEERID + 1))
    echo "Peer $PEERID ($1) PID: ${PIDS[$1]} CPU: $CPU"
}

# start_leecher <name> <hash> <time>
function start_leecher {
    local STORE=$TMP_DIR/peers/$1
    
    mkdir -p $STORE
    mkdir -p $LOGS_DIR/$1
    echo "Starting peer $1 (leecher) for hash $2"
    ls -alh $STORE
    if $DEBUG; then
        DBGSTR="--debug"
    else
        DBGSTR=""
    fi
    # round robin affinity using the optionally supplied array
    local CPU=${AFNTY[$PEERID % ${#AFNTY[@]}]}
    local UPRATE=$(eval "echo \$UPRATE_$1")
    local DOWNRATE=$(eval "echo \$DOWNRATE_$1")
    $DIR/process_guard.py -c "taskset -c $CPU $SWIFT $UPRATE $DOWNRATE -o $STORE -h $2 -t 127.0.0.1:1337 -z 1024 --progress $DBGSTR" -t $3 -m $LOGS_DIR/$1 -o $LOGS_DIR/$1 &
    PIDS[$1]=$!
    PEERID=$(($PEERID + 1))
    echo "Peer $PEERID ($1) PID: ${PIDS[$1]} CPU: $CPU"
}

# ------------------------------------------------------------------------------

echo "Experiment time: $TIME"

prepare_seeder_files seeder
#UPRATE_seeder="--uprate 512"
start_seeder seeder $TIME
sleep `echo "$TIME*0.1" | bc` # wait 10% of total time
#DOWNRATE_leecher1="--downrate 256"
start_leecher leecher1 ${HASHES[seeder]} $(printf "%.0f" $(echo "$TIME-$TIME*0.1" | bc))
sleep `echo "$TIME*0.1" | bc` # wait 10% of total time
start_leecher leecher2 ${HASHES[seeder]} $(printf "%.0f" $(echo "$TIME-$TIME*0.2" | bc))

echo "Waiting for PIDs: ${PIDS[*]}"

wait ${PIDS[leecher1]}
wait ${PIDS[leecher2]}
wait ${PIDS[seeder]}

diff -s $TMP_DIR/peers/seeder/${HASHES[seeder]} $TMP_DIR/peers/leecher1/${HASHES[seeder]}
diff -s $TMP_DIR/peers/seeder/${HASHES[seeder]} $TMP_DIR/peers/leecher2/${HASHES[seeder]}

# ------------------------------------------------------------------------------

for peer in $PIDS; do
    echo $peer
done

$DIR/parse_logs.py $LOGS_DIR/seeder
$DIR/parse_logs.py $LOGS_DIR/leecher1
$DIR/parse_logs.py $LOGS_DIR/leecher2

gnuplot -e "logdir='$LOGS_DIR/seeder';peername='seeder';plotsdir='$PLOTS_DIR'" $DIR/resource_usage.gnuplot
gnuplot -e "logdir='$LOGS_DIR/leecher1';peername='leecher1';plotsdir='$PLOTS_DIR'" $DIR/resource_usage.gnuplot
gnuplot -e "logdir='$LOGS_DIR/leecher2';peername='leecher2';plotsdir='$PLOTS_DIR'" $DIR/resource_usage.gnuplot

gnuplot -e "peers='leecher1 leecher2';logdir='$LOGS_DIR';plotsdir='$PLOTS_DIR'" $DIR/speed.gnuplot

rm $PLOTS_LAST_DIR/*
cp $PLOTS_DIR/* $PLOTS_LAST_DIR/

# ------------------------------------------------------------------------------
