import time
import argparse
import sys
import os
from random import randint
from shutil import rmtree

# logging config file only when not used as a library
import logging
if __name__ == "__main__":
    import logging.config
    logger_conf = os.path.abspath(os.environ.get("LOGGER_CONF", "logger.conf"))
    print "Logger using configuration file: " + logger_conf
    logging.config.fileConfig(logger_conf)
logger = logging.getLogger(__name__)

# Tribler should be in PYTHONPATH
from Tribler.dispersy.crypto import ec_generate_key
from Tribler.dispersy.crypto import ec_to_private_bin, ec_to_public_bin
from Tribler.community.bartercast3.community import BarterCommunity
from Tribler.community.bartercast3.script import DummySwiftProcess

def create_bc3_community(dispersy):
    ec = ec_generate_key(u"very-low")
    private_key = ec_to_private_bin(ec)
    public_key = ec_to_public_bin(ec)

    my_member = dispersy.get_member(public_key, private_key)
    c = BarterCommunity.create_community(dispersy, my_member, DummySwiftProcess())
    logger.info("created community with cid " + c.cid.encode('hex'))
    
    with open(os.path.join(os.environ["PROJECTROOT"], "tmp", "bc3_master"), "w") as f:
        print >>f, c._master_member.public_key.encode("hex"), c._master_member.mid.encode("hex")

BOOTSTRAPTRIBLER_FILE = "bootstraptribler.txt"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Creates a new BC3 community.')
    parser.add_argument("-l", "--listen", metavar="IP", help='local listen ip')
    parser.add_argument("-i", "--tracker-ip", default="127.0.0.1", metavar="IP", help='Dispersy tracker IP')
    parser.add_argument("-p", "--tracker-port", type=int, default=6421, metavar="PORT", help='Dispersy tracker port')
    args = parser.parse_args()

    from Tribler.dispersy.script import ScriptBase
    from Tribler.dispersy.member import Member
    from Tribler.dispersy.callback import Callback
    from Tribler.dispersy.dispersy import Dispersy
    from Tribler.dispersy.endpoint import StandaloneEndpoint

    with open(BOOTSTRAPTRIBLER_FILE, "w") as f:
        print >> f, args.tracker_ip, args.tracker_port

    # start in-memory Dispersy
    callback = Callback('Dispersy')
    if args.listen != None:
        endpoint = StandaloneEndpoint(randint(10000, 20000), args.listen)
    else:
        endpoint = StandaloneEndpoint(randint(10000, 20000))
    dispersy = Dispersy(callback, endpoint, u'.')
    dispersy.start()
    logger.info("Dispersy is listening on " + repr(dispersy.lan_address))

    callback.call(create_bc3_community, (dispersy,))

    # wait
    # TODO(vladum): Wait until community is created (or just some time).
    # try:
    #     while callback.is_running:
    #         time.sleep(5.0)
    # except KeyboardInterrupt:
    #     logger.info("shutting down")
    # finally:
    dispersy.stop()
    # cleanup filesystem
    os.unlink(BOOTSTRAPTRIBLER_FILE)
    rmtree("./sqlite")
