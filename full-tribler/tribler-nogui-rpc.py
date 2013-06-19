import sys
import shutil
import time
import tempfile
import random
import os
import getopt
import logging.config
from traceback import print_exc
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

TRIBLERPATH = os.environ['TRIBLERPATH']
sys.path += [TRIBLERPATH]

from Tribler.Core.API import *
from Tribler.Core.__init__ import version, report_email

logging.config.fileConfig('logger.conf')

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
    def __init__(self, port):
        self.sscfg = SessionStartupConfig()
        self.statedir = tempfile.mkdtemp()
        self.sscfg.set_swift_path(os.path.join(TRIBLERPATH, 'swift'))
        self.sscfg.set_swift_proc(True)
        self.sscfg.set_state_dir(self.statedir)
        self.sscfg.set_listen_port(port)
        self.sscfg.set_swift_tunnel_listen_port(port)
        self.sscfg.set_megacache(False)
        self.sscfg.set_dispersy(True)

    def start(self):
        self.s = Session(self.sscfg)
        self.s.start()

    def seed(self, filename):
        sdef = SwiftDef()
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
        dscfg.set_dest_dir('.')
        dscfg.set_swift_meta_dir('.')
        d = self.s.start_download(sdef, dscfg)
        d.set_state_callback(download_state_callback, getpeerlist=[])

        # TODO: Add leeching download to some list.

        return 'Leeching from:', url

    def shutdown(self):
        self.s.shutdown()
        time.sleep(3)
        shutil.rmtree(self.statedir)

def main():
    if len(sys.argv) < 2:
        print 'Usage:', sys.argv[0], '<rpcport>'
        exit(1)

    server = SimpleXMLRPCServer(
        ("0.0.0.0", 8000),
        requestHandler=SimpleXMLRPCRequestHandler)
    server.register_introspection_functions()

    t = NoGuiTribler(int(sys.argv[1]))
    t.start()

    server.register_instance(t)

    server.serve_forever()
    time.sleep(2)
    t.shutdown()

if __name__ == "__main__":
    main()
