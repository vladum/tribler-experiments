import argparse
import sys
import signal
import os

import logging
import logging.config
logger_conf = os.path.abspath(os.environ.get("LOGGER_CONF", "logger.conf"))
print "Logger using configuration file: " + logger_conf
logging.config.fileConfig(logger_conf)
logger = logging.getLogger(__name__)

# Tribler should be in PYTHONPATH
from Tribler.dispersy.tool.tracker import TrackerDispersy, setup_dispersy
from Tribler.dispersy.tool.mainthreadcallback import MainThreadCallback
from Tribler.dispersy.endpoint import StandaloneEndpoint

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Runs a Dispersy tracker.')
    parser.add_argument("--ip", metavar="IP")
    parser.add_argument("--port", type=int, default=6421, metavar="PORT")
    args = parser.parse_args()

    # start Dispersy
    dispersy = TrackerDispersy(MainThreadCallback("Dispersy"), StandaloneEndpoint(args.port, args.ip), u".", False)
    dispersy.callback.register(setup_dispersy, (dispersy,))
    dispersy.start()

    def signal_handler(sig, frame):
        print "Received signal '", sig, "' in", frame, "(shutting down)"
        dispersy.stop(timeout=0.0)
    signal.signal(signal.SIGINT, signal_handler)

    # wait forever
    dispersy.callback.loop()
