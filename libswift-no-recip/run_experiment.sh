#!/bin/bash

[ -z $TIME ] && TIME=30
[ -z $SWIFT ] && SWIFT=./swift

echo "Experiment time: $TIME"
$SWIFT
