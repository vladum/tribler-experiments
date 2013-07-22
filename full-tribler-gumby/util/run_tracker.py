import argparse
import sys
import signal

import logging
import logging.config
logging.config.fileConfig("logger.conf")
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Runs a Dispersy tracker.')
    parser.add_argument("-t", "--tribler", metavar="PATH", required=True, help='tribler root dir')    
    parser.add_argument("--ip", metavar="IP")
    parser.add_argument("--port", type=int, default=6421, metavar="PORT")
    args = parser.parse_args()

    sys.path += [args.tribler]
    from Tribler.dispersy.tool.tracker import TrackerDispersy, setup_dispersy
    from Tribler.dispersy.tool.mainthreadcallback import MainThreadCallback
    from Tribler.dispersy.endpoint import StandaloneEndpoint

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
