#!/usr/bin/env python

import sys
import os
from twisted.internet import reactor

from gumby.config import ConfigClientFactory, get_config_server_endpoint

def start_experiment(config):
    print "\n\nConfiguration received. Starting experiment."
    print config

def main():
    factory = ConfigClientFactory()
    factory.onConfigReceived(start_experiment)

    ip, port = get_config_server_endpoint()
    reactor.connectTCP(ip, port, factory)

    # run experiment for a few seconds
    reactor.callLater(4, reactor.stop)
    reactor.run()

if __name__ == "__main__":
    main()
