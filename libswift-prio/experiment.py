import os
import shlex
import time
from socket import socket, AF_INET, SOCK_DGRAM
from subprocess import call, Popen
from threading import Thread

TMPDIR = './tmp'
LOGSDIR = os.path.join(TMPDIR, 'logs')
SWIFTBINARY = './swift'

class LocalSwiftInstance():
    def __init__(self, listen, cmdgw, filename):
        self.name = 'seeder'
        self.listen = listen
        self.filename = filename
        self._cwd = None
        self.__cmdgw_sock = socket(AF_INET, SOCK_DGRAM)
        [self.__cmdgw_ip, self.__cmdgw_port] = cmdgw.split(':')
        self._make_dirs()
    
    def _make_dirs(self):
        self._dir = os.path.join(TMPDIR, self.name)
        self._stderr = os.path.join(LOGSDIR, self.name, 'stderr.log')
        self._stdout = os.path.join(LOGSDIR, self.name, 'stdout.log')
    
    def start_process(self):
        cmd = [
            os.path.abspath(SWIFTBINARY),
            '-l', self.listen, 
            '-p', 
            '-n', os.path.abspath(self._dir),
            '-f', os.path.abspath(self.filename),
            '-B'
        ]
        print 'launching:', ' '.join(cmd)
        fstdout = open(self._stdout, 'w')
        fstderr = open(self._stderr, 'w')
        self.process = Popen(
            args=cmd,
            stdout=fstdout,
            stderr=fstderr,
            cwd=self._cwd
        )
        print 'process started: name =', self.name,
        print ' pid =', self.process.pid
        
    def get_roothash_blocking(self):
        f = open(self._stdout, 'r')
        while True:
            line = f.readline()
            if line == '':
                # end of file
                f.seek(0, 0)
                continue
            r = line.split(':')
            if r[0] == 'Root hash':
                return r[1][1:-1]
    
    def send_peer_weigths(self, weights):
        msg = ''.join([
            ip + ':' + str(port) + ':' + str(weight) 
            for (ip, port, weight) in weights
        ])
        self.__cmdgw_sock.sendto(
            'RECIPROCITY PEERWEIGHTS ' + msg,
            (self.__cmdgw_ip, int(self.__cmdgw_port)))

class Seeder(LocalSwiftInstance):
    pass

class Leecher(LocalSwiftInstance):
    def __init__(self, tracker, cmdgw, roothash, name):
        LocalSwiftInstance.__init__(self, tracker, cmdgw, roothash)
        self.name = name
        # listen and filename is also tracker and roothash for leechers
        self.roothash = roothash
        self.tracker = tracker
        self._make_dirs()
    
    def start_process(self):
        cmd = [
            os.path.abspath(SWIFTBINARY),
            '-t', self.tracker, 
            '-p', 
            '-n', os.path.abspath(self._dir),
            '-h', self.roothash,
            '-B',
            '-y', '1024' # downrate in KiB
        ]
        print 'launching:', ' '.join(cmd)
        fstdout = open(self._stdout, 'w')
        fstderr = open(self._stderr, 'w')
        try:
            self.process = Popen(
                args=cmd,
                stdout=fstdout,
                stderr=fstderr,
                cwd=self._cwd
            )
        except OSError as e:
            print self._cwd
            raise e
        print 'process started: name =', self.name,
        print ' pid =', self.process.pid

def silent_mkdir(d):
    try:
        os.mkdir(d)
    except OSError as _:
        # Do nothing if already exists.
        pass

def set_up_files():
    # TODO(vladum): Move some of these to the objects.
    silent_mkdir(TMPDIR)
    silent_mkdir(os.path.join(TMPDIR, 'seeder'))
    silent_mkdir(os.path.join(TMPDIR, 'leecher1'))
    silent_mkdir(LOGSDIR)
    silent_mkdir(os.path.join(LOGSDIR, 'seeder'))
    silent_mkdir(os.path.join(LOGSDIR, 'leecher1'))

    dummy_file = os.path.join(TMPDIR, 'seeder', 'somefile')
    # 1GiB file
    call(['dd', 'if=/dev/urandom', 'of=' + dummy_file, 'bs=16M',
          'count=1']) # TODO(vladum): count=64

    return dummy_file

def echo_leecher_stderr(filename):
    f = open(filename, 'r')
    while True:
        line = f.readline()
        if line == '':
            break
        if line.lower().startswith('done'):
            print line[:-1]
    f.close()
    print 'finished!'

if __name__ == '__main__':
    dummy_file = set_up_files()

    sipport = '127.0.0.1:10000'
    seeder = Seeder(sipport, '127.0.0.1:10001', dummy_file)
    seeder.start_process()

    roothash = seeder.get_roothash_blocking()
    print 'got roothash from seeder:', roothash

    leecher1 = Leecher(sipport, '127.0.0.2:20001', roothash, 'leecher1')
    leecher1._cwd = os.path.abspath(os.path.join(TMPDIR, 'leecher1'))
    os.mkfifo(leecher1._stderr)
    t = Thread(target=echo_leecher_stderr, args=(leecher1._stderr,)).start()
    leecher1.start_process()

    time.sleep(5)
    
    leecher1.process.kill()
