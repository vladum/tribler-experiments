import sys
import shutil
import time
import tempfile
import random
import os
import getopt
import logging.config
from traceback import print_exc
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

# prepare ROOTDIR
UNIQUE = sys.argv[3] + '-' + sys.argv[1]
try:
    ROOTDIR = os.path.abspath(os.environ['ROOTDIR'])
except KeyError:
    ROOTDIR = os.path.join('/local', os.environ['USER'], UNIQUE)
if not os.path.exists(ROOTDIR):
    os.mkdir(ROOTDIR)
OLDCWD = os.getcwd()
os.chdir(ROOTDIR)

logging.config.fileConfig(os.path.join(OLDCWD, 'logger.conf'))

TRIBLERPATH = os.path.join(OLDCWD, os.environ['TRIBLERPATH'])
sys.path += [TRIBLERPATH]

from Tribler.Core.API import *

def download_state_callback(ds):
    d = ds.get_download()
    print >> sys.stderr, '%s %s %5.2f%% %s up %8.2fKB/s down %8.2fKB/s' % \
        (d.get_def().get_name(),
        dlstatus_strings[ds.get_status()],
        ds.get_progress() * 100,
        ds.get_error(),
        ds.get_current_speed(UPLOAD),
        ds.get_current_speed(DOWNLOAD))

    return (1.0, False)

class NoGuiTribler:
    def __init__(self, id, swiftport):
        self.peerid = id
        self.sscfg = SessionStartupConfig()
        self.statedir = os.path.join(ROOTDIR, 'state' + self.peerid)
        self.sscfg.set_swift_path(os.path.join(TRIBLERPATH, 'swift'))
        self.sscfg.set_swift_proc(True)
        self.sscfg.set_state_dir(self.statedir)
        
        self.sscfg.set_swift_tunnel_listen_port(swiftport)
        self.sscfg.sessconfig['dispersy-tunnel-over-swift'] = True

        self.sscfg.set_libtorrent(False)
        self.sscfg.set_megacache(False)
        self.sscfg.set_torrent_collecting(False)
        self.sscfg.set_mainline_dht(False)
        self.sscfg.set_dispersy(True)

    def start(self):
        self.s = Session(self.sscfg)
        self.s.start()

    def seed(self, filename):
        sdef = SwiftDef()
        # TODO: change these
        sdef.set_tracker("127.0.0.1:%d" % self.s.get_swift_dht_listen_port())
        sdef.add_content(filename)
        sdef.finalize(self.s.get_swift_path(), destdir=destdir)

        dscfg = DownloadStartupConfig()
        dscfg.set_dest_dir(filename)
        dscfg.set_swift_meta_dir(destdir)

        d = self.s.start_download(sdef, dscfg)
        d.set_state_callback(download_state_callback, getpeerlist=[])

        # TODO: Add seeding download to some list.

        return 'Seeding file:', filename

    def leech(self, url):
        sdef = SwiftDef.load_from_url(url)

        dscfg = DownloadStartupConfig()
        dscfg.set_dest_dir(os.path.join(ROOTDIR, 'dwload' + self.peerid))
        dscfg.set_swift_meta_dir(os.path.join(ROOTDIR, 'dwload' + self.peerid))
        d = self.s.start_download(sdef, dscfg)
        d.set_state_callback(download_state_callback, getpeerlist=[])

        # TODO: Add leeching download to some list.

        return 'Leeching from:', url

    def shutdown(self):
        self.s.shutdown()
        time.sleep(3)
        shutil.rmtree(self.statedir)

RPCPORT = 8000
SWIFTPORT = 10001
PEERID = '0'

def main():
    server = SimpleXMLRPCServer(
        ("0.0.0.0", RPCPORT),
        requestHandler=SimpleXMLRPCRequestHandler)
    server.register_introspection_functions()

    t = NoGuiTribler(PEERID, SWIFTPORT)
    t.start()

    server.register_instance(t)

    server.serve_forever()
    time.sleep(2)
    t.shutdown()

if __name__ == "__main__":
    main()
