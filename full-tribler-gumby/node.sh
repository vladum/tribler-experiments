#!/bin/bash

mkdir -p `pwd`/output/logs
TRIBLER_LOGSDIR=`pwd`/output/logs LOGGER_CONF=logger.conf.node python node.py $@
