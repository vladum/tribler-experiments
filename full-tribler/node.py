#!/usr/bin/env python

import sys
# TODO: Replace zmq with XMLRPC.
import zmq
import random
import time
from subprocess import call

from das4 import *
from experiment import run

STAGE_MASTER_PORT = '5556'
SETTINGS = {
    'peerid': sys.argv[1], # we'll use the node id set by panda
    'ip': get_current_node_ip(),
    'swiftport': '1234',
    'rpcport': '2345',
    # TODO: Others? Dispersy etc?
}

def report_settings():
    # Send this node's IPs and ports to the experiment controller.
    context = zmq.Context()
    socket = context.socket(zmq.REQ) # request
    socket.connect('tcp://' + get_master_node_ip() + ':' + STAGE_MASTER_PORT)
    socket.send(repr(SETTINGS))
    socket.recv()

def start_tribler_nogui():
    print 'Starting Tribler NOGUI.'

def stage_master_main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind('tcp://*:' + STAGE_MASTER_PORT)
    i = 0
    settings = []
    while i < get_nodes_no() - 1:
        s = eval(socket.recv())
        settings += [s]
        print 'Received settings:', s
        socket.send('ACK')
        i += 1
    print 'Got all peer settings:', settings, '. Starting experiment.'
    run(settings)

def normal_node_main():
    report_settings()
    start_tribler_nogui()
    print 'Done.'

if __name__ == '__main__':
    if get_current_node() == get_master_node():
        stage_master_main()
    else:
        normal_node_main()


