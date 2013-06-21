#!/usr/bin/env python

import time
import xmlrpclib

def swift_uri(peer, roothash):
    return 'tswift://' + peer['ip'] + ':' + str(peer['swiftport']) + '/' + roothash

def generate_file(peer, size=0):
    '''Generate a file of <size> MB.'''
    print 'Generating file on peer', peer
    s = xmlrpclib.ServerProxy(peer['ip'] + str(peer['rpcport']))
    return s.generate_file(size)

def start_download(peer, uri):
    pass

def kill(peer):
    print 'Killing', peer

def run(peers):
    print 'Starting experiment with settings:', peers
    time.sleep(2)

    roothash = generate_file(peers[0], 10)
    print 'roothash:', roothash
    time.sleep(2)
    start_download(peers[1], swift_uri(peers[0], roothash))
    time.sleep(10)

    for p in peers:
        kill(p)

