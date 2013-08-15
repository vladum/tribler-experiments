#!/usr/bin/env python

from os import environ, mkdir, path
from sys import stderr
from collections import namedtuple
from datetime import date
from time import strftime, localtime

# TODO: Multiple scenario files in one campaign.
Scenario = namedtuple('Scenario', [
    'scenario_file_template',
    'campaign_file_template',
    'scenario_file',
    'campaign_file'
])

SCENARIOS = [
    Scenario('templates/test.s.tpl', 'templates/test.c.tpl', 'test.s', 'test.c')
]

def read_environ():
    global P2PTESTFRAMEWORK, SWIFT, LFS
    try:
        P2PTESTFRAMEWORK = environ['P2PTESTFRAMEWORK']
        SWIFT = environ['SWIFT']
        LFS = environ['LFS']
    except KeyError as e:
        print >>stderr, 'Please set', e, 'environment variable.'
        exit(1)

def check_environ():
    # TODO: Check if paths are valid.
    if False:
        print >>stderr, 'Please set proper environment vars.'
        exit(1)

def make_config_dir():
    dirname = 'config-' + strftime('%Y-%m-%d-%H-%M-%S-%Z', localtime())
    try:
        mkdir(dirname)
    except OSError:
        print >>stderr, 'Config dir already exists.'
        exit(1)
    return dirname

def gen_config_files(configdir, scenario):
    print 'Generating config files for scenario:', scenario

    with open(scenario.scenario_file_template, 'r') as tpl,\
         open(path.join(configdir, scenario.scenario_file), 'w') as f:
        print >>f, tpl.read().format(swiftdir=SWIFT, lfsdir=LFS)

    with open(scenario.campaign_file_template, 'r') as tpl,\
         open(path.join(configdir, scenario.campaign_file), 'w') as f:
        print >>f, tpl.read().format(swiftdir=SWIFT, lfsdir=LFS)

def run_campaign(config, scenario):
    print 'Running campaign for:', scenario

    # TODO

def main():
    read_environ()
    check_environ()

    print 'P2P Test Framework in:', P2PTESTFRAMEWORK
    print 'libswift in:', SWIFT
    print 'LFS in:', LFS

    configdir = make_config_dir()
    print 'Config dir is:', configdir

    for s in SCENARIOS:
        gen_config_files(configdir, s)
        run_campaign(configdir, s)

if __name__ == '__main__':
    main()
