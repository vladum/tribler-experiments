#!/usr/bin/env python

import time

def swift_uri(peer, roothash):
    return 'tswift://' + peer['ip'] + ':' + str(peer['swiftport']) + '/' + roothash

def generate_file(peer, size=0):
    '''Generate a file of <size> MB.'''
    # TODO: XMLRPC send
    print 'Generating file on peer', peer
    return 'deadbeef12deadbeef12deadbeef12deadbeef12'

def start_download(peer, uri):
    pass

def kill(peer):
    print 'Killing', peer

def run(peers):
    print 'Starting experiment with settings:', peers
    time.sleep(2)

    roothash = generate_file(peers[0], 100)
    time.sleep(2)
    start_download(peers[1], swift_uri(peers[0], roothash))
    time.sleep(10)

    for p in peers:
        kill(p)

