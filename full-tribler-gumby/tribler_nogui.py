import sys
import shutil
import time
import tempfile
import random
import os
import getopt
import logging.config
from subprocess import call
from traceback import print_exc

# TODO: Use abs.
TRIBLERPATH = os.path.join(
    "/home",
    os.environ["USER"],
    os.environ['TRIBLERPATH']
)
sys.path += [TRIBLERPATH]
from Tribler.Core.API import *

def download_state_callback(ds):
    """
    Logs download progress while the experiment if running.
    """
    d = ds.get_download()
    print >> sys.stderr, '%s %s %5.2f%% %s up %8.2fKB/s down %8.2fKB/s' % \
        (d.get_def().get_name(),
        dlstatus_strings[ds.get_status()],
        ds.get_progress() * 100,
        ds.get_error(),
        ds.get_current_speed(UPLOAD),
        ds.get_current_speed(DOWNLOAD))

    return (1.0, False)

class TriblerNoGui:
    """
    This only runs Tribler's Session. No GUI, no wx stuff. It also defines
    methods that will be called while the experiment's scenario unfolds.

    Available scenario actions:
        * generate_file
        * seed
        * leech
    """
    def __init__(self, id, swiftport, rootdir):
        """
        This only prepares the SessionStartupConfig object. Call start() to
        actually start Tribler.
        """
        self.rootdir = rootdir
        if not os.path.exists(self.rootdir):
            os.makedirs(self.rootdir)
        os.chdir(rootdir)

        self.peerid = id
        self.statedir = os.path.join(self.rootdir, 'state' + self.peerid)

        self.sscfg = SessionStartupConfig()
        self.sscfg.set_state_dir(self.statedir)
        self.sscfg.set_swift_path(
            os.path.join(TRIBLERPATH, 'Tribler', 'SwiftEngine', 'swift')
        )
        self.sscfg.set_swift_tunnel_listen_port(swiftport)
        self.sscfg.set_dispersy_tunnel_over_swift(True)

        # we only play with swift and dispersy in this experiment
        self.sscfg.set_swift_proc(True)
        self.sscfg.set_dispersy(True)

        self.sscfg.set_libtorrent(False)
        self.sscfg.set_megacache(False)
        self.sscfg.set_torrent_collecting(False)
        self.sscfg.set_mainline_dht(False)

    def start(self):
        self.s = Session(self.sscfg)
        self.s.start()

    def shutdown(self):
        self.s.shutdown()
        time.sleep(3)
        shutil.rmtree(self.statedir)

    def generate_file(self, size):
        call(['dd', 'if=/dev/urandom', 'of=' + self.rootdir + '/file', 'bs=1M', 'count=' + str(size)])
        return 'deadbeef12deadbeef12deadbeef12deadbeef12'

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

    def leech(self, url):
        sdef = SwiftDef.load_from_url(url)

        dscfg = DownloadStartupConfig()
        dscfg.set_dest_dir(os.path.join(self.rootdir, 'dwload' + self.peerid))
        dscfg.set_swift_meta_dir(os.path.join(self.rootdir, 'dwload' + self.peerid))
        d = self.s.start_download(sdef, dscfg)
        d.set_state_callback(download_state_callback, getpeerlist=[])

        # TODO: Add leeching download to some list.

    def test_method(self, param="bau"):
        print "Test method called at", time.time(), "by peer", self.peerid, "with param", param
