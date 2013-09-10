import sys
import os
from shutil import copyfile
from time import time, sleep
from twisted.internet import reactor

from gumby.config import ConfigClientFactory, get_config_server_endpoint
from gumby.scenario import ScenarioRunner

from tribler_nogui import TriblerNoGui

import logging
import logging.config
logger_conf = os.path.abspath(os.environ.get("LOGGER_CONF", "logger.conf"))
print "Logger using configuration file: " + logger_conf
logging.config.fileConfig(logger_conf)
logger = logging.getLogger(__name__)

def start_scenario(t):
    print "Starting scenario."
    st = ScenarioRunner(
        os.path.join(os.environ["PROJECTROOT"], os.environ["SCENARIO_FILE"]),
        int(t.peerid)
    )
    st.register(t.test_method)
    st.register(t.generate_file)
    st.register(t.seed)
    st.register(t.leech)
    st.run()

def start_experiment(peerid, swiftport, config):
    rootdir = os.path.join(
        "/local/",
        os.environ["USER"],
        os.environ["UNIQUE"] + "-" + str(peerid)
    )
    if not os.path.exists(rootdir):
        os.makedirs(rootdir)
    copyfile(
        os.path.join(
            "/home/",
            os.environ["USER"],
            os.environ["BOOTSTRAPTRIBLER_FILE"]
        ),
        os.path.join(rootdir, "bootstraptribler.txt")
    )
    with open("/etc/HOSTNAME") as f:
        node_hostname = f.read()
    print str(peerid) + ": Starting TriblerNoGui on " + node_hostname
    
    t = TriblerNoGui(str(peerid), swiftport, rootdir, config)
    t.start()
    print str(peerid) + ": TriblerNoGui running on port " + str(swiftport)

    start_scenario(t)

def prepare_experiment(config):
    print config['my']['id'] + ": Configuration received."

    myid = int(config["my"]["id"])
    port = int(config["my"]["port"])
    start_timestamp = int(config["my"]["start_timestamp"])
    delay = start_timestamp - time()
    print config['my']['id'] + ": TriblerNoGui will start in " + str(delay) + " seconds."
    # TODO(vladum): Do not do this here. The scenario should handle this.
    reactor.callLater(delay, start_experiment, myid, port, config)

def main():
    factory = ConfigClientFactory()
    factory.onConfigReceived(prepare_experiment)

    ip, port = get_config_server_endpoint()
    reactor.connectTCP(ip, port, factory)

    # run experiment for a few seconds
    # reactor.callLater(4, reactor.stop)
    reactor.run()

if __name__ == "__main__":
    main()
