#!/bin/bash

SBIN="swift-VoD-merge"
#SBIN="libswift-vladum"

TAG="$(date -Iminutes | tr "+:" "-")-$SBIN"

export SWIFTBINARY=../../$SBIN/swift
export TMPDIR="./tmp-$TAG"

echo "TMPDIR is: $TMPDIR"

python experiment.py

# get the roothash
HASH=$(cat $TMPDIR/seeder/somefile.mbinmap | head -2 | tail -1 | cut -d " " -f 3 | tr -s " ")

# diff the files
diff $TMPDIR/seeder/somefile $TMPDIR/leecher1/$HASH
diff $TMPDIR/seeder/somefile $TMPDIR/leecher2/$HASH

# delete big files
rm $TMPDIR/seeder/somefile
rm $TMPDIR/leecher1/$HASH
rm $TMPDIR/leecher2/$HASH

# plot
./plot.sh

# run vdbg
mkdir $TMPDIR/vdbg/
PEERLOG="$TMPDIR/leecher1/leecher1.log" ../vdbg/swiftdbg.py > $TMPDIR/vdbg/leecher1.html
PEERLOG="$TMPDIR/leecher2/leecher2.log" ../vdbg/swiftdbg.py > $TMPDIR/vdbg/leecher2.html
#PEERLOG="$TMPDIR/seeder/seeder.log" ../vdbg/swiftdbg.py > $TMPDIR/vdbg/seeder.html

firefox -new-tab $TMPDIR/vdbg/leecher1.html &
sleep 1
firefox -new-tab $TMPDIR/vdbg/leecher2.html &
#xdg-open seeder.html
