import os
import shlex
import time
import signal
import sys
import operator
from socket import socket, AF_INET, SOCK_STREAM
from subprocess import call, Popen
from threading import Thread

try:
    TMPDIR = os.environ['TMPDIR']
except KeyError:
    TMPDIR = './tmp'

try:
    SWIFTBINARY = os.environ['SWIFTBINARY']
except KeyError:
    SWIFTBINARY = '/home/vlad/work/thesis/swift-VoD-merge/swift'

LOGSDIR = os.path.join(TMPDIR, 'logs')
PLOTDIR = os.path.join(TMPDIR, 'plots')

TM = [60 * 60 * 1000000, 60 * 1000000, 1000000, 1000, 1]

def parse_peer_logs(names=['seeder', 'leecher1', 'leecher2']):
    starttime = None # seeder will have the min time
    for name in names:
        dstf = open(os.path.join(PLOTDIR, name + '.plog'), 'w')
        srcf = open(os.path.join(LOGSDIR, name, 'stderr.log'), 'r')

        speed_up = 0
        speed_down = 0
        prev_bytes_up = 0
        prev_bytes_down = 0
        prev_timestamp_up = 0
        prev_timestamp_down = 0
        prev_diff_up = 0
        prev_diff_down = 0

        for line in srcf.readlines():
            l = line.split(' ')
            if l[0] == 'done' or l[0] == 'SEED' or l[0] == 'DONE':
                t = map(operator.mul, TM, [int(x) for x in l[1].split('_')])
                currenttime = reduce(operator.add, t, 0)
                if starttime == None:
                    # first line (min time; from the seeder)
                    starttime = currenttime
                if currenttime < starttime:
                    # day changed
                    currenttime += 24 * 60 * 60 * 1000000

                timestamp = float(currenttime - starttime) / 1000
                if name == 'seeder':
                    raw_bytes_up = int(l[4])
                    bytes_up = int(l[8])
                    raw_bytes_down = int(l[13])
                    bytes_down = int(l[17])
                    progress = '-'
                else:
                    raw_bytes_up = '-'
                    bytes_up = int(l[9])
                    raw_bytes_down = '-'
                    bytes_down = int(l[14])
                    progress = float(l[2]) / float(l[4])

                try:
                    diff_up = bytes_up - prev_bytes_up
                    if not diff_up:
                        raise ZeroDivisionError
                    speed_up = (diff_up / \
                        float(timestamp - prev_timestamp_up)) * 1000 # per sec
                    prev_timestamp_up = timestamp
                    prev_bytes_up = bytes_up
                    prev_diff_up = diff_up
                except ZeroDivisionError:
                    pass
                    #speed_up = 0
                try:
                    diff_down = bytes_down - prev_bytes_down
                    if not diff_down:
                        raise ZeroDivisionError
                    speed_down = (diff_down / \
                        float(timestamp - prev_timestamp_down)) * 1000 # per sec
                    prev_timestamp_down = timestamp
                    prev_bytes_down = bytes_down
                    prev_diff_down = diff_down
                except ZeroDivisionError:
                    pass
                    #speed_down = 0

                print >>dstf, timestamp, progress, raw_bytes_up, bytes_up, \
                    raw_bytes_down, bytes_down, speed_up, speed_down

        dstf.close()
        srcf.close()

class LocalSwiftInstance():
    def __init__(self, listen, cmdgw, filename):
        self.name = 'seeder'
        self.listen = listen
        self.filename = filename
        self._cwd = None
        [self.__cmdgw_ip, self.__cmdgw_port] = cmdgw.split(':')
        self._make_dirs()
    
    def _make_dirs(self):
        self._dir = os.path.join(TMPDIR, self.name)
        self._stderr = os.path.join(LOGSDIR, self.name, 'stderr.log')
        self._stdout = os.path.join(LOGSDIR, self.name, 'stdout.log')
    
    def start_process(self):
        cmd = [
            os.path.abspath(SWIFTBINARY),
            '-c', self.__cmdgw_ip + ':' + str(self.__cmdgw_port),
            '-l', self.listen, 
            '-p', 
            '-n', os.path.abspath(self._dir),
            '-d', os.path.abspath(self._dir),
            #'-u', '102400', #uprate
            #'-B',
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
        time.sleep(2)
        self.__cmdgw_sock = socket(AF_INET, SOCK_STREAM)
        self.__cmdgw_sock.connect((self.__cmdgw_ip, int(self.__cmdgw_port)))
        
    def get_roothash_blocking(self):
        while True:
            try:
                f = open(os.path.join(self._dir, 'somefile.mbinmap'), 'r')
                break
            except IOError as _:
                print 'retrying to open .mbinmap file'
                time.sleep(1)
                continue
        time.sleep(2)
        while True:
            line = f.readline()
            if line == '':
                # end of file
                f.seek(0, 0)
                continue
            r = line.split(' ')
            if r[0] == 'root':
                return r[2][:-1]
    
    def send_peer_weigths(self, weights):
        msg = ' '.join([
            ip + ':' + str(port) + ':' + str(weight) 
            for (ip, port, weight) in weights
        ])
        msg = 'RECIPROCITY PEERWEIGHTS ' + msg
        print 'sending:', msg, 'to:', (self.__cmdgw_ip, int(self.__cmdgw_port))
        self.__cmdgw_sock.send(msg)
    
    def set_maxspeed_upload(self, speed, roothash='0' * 20):
        msg = 'MAXSPEED ' + roothash + ' UPLOAD ' + repr(speed)
        print 'sending:', msg, 'to:', (self.__cmdgw_ip, int(self.__cmdgw_port))
        self.__cmdgw_sock.send(msg + '\r\n')

    def send_start(self):
        msg = 'START \r\n'
        self.__cmdgw_sock.send(msg)

class Seeder(LocalSwiftInstance):
    pass

class Leecher(LocalSwiftInstance):
    def __init__(self, tracker, cmdgw, roothash, name, listenport):
        LocalSwiftInstance.__init__(self, tracker, cmdgw, roothash)
        self.name = name
        # listen and filename is also tracker and roothash for leechers
        self.roothash = roothash
        self.tracker = tracker
        self.listenport = listenport
        self._make_dirs()
    
    def start_process(self):
        cmd = [
            os.path.abspath(SWIFTBINARY),
            '-t', self.tracker, 
            '-l', self.listenport,
            '-p',
            '-n', os.path.abspath(self._dir),
            '-h', self.roothash,
            '--debug',
            '-D' + self.name + '.log',
            #'-u', '0' # uprate in KiB
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
    silent_mkdir(os.path.join(TMPDIR, 'leecher2'))
    silent_mkdir(LOGSDIR)
    silent_mkdir(os.path.join(LOGSDIR, 'seeder'))
    silent_mkdir(os.path.join(LOGSDIR, 'leecher1'))
    silent_mkdir(os.path.join(LOGSDIR, 'leecher2'))
    silent_mkdir(PLOTDIR)

    dummy_file = os.path.join(TMPDIR, 'seeder', 'somefile')
    # 1GiB file
    call(['dd', 'if=/dev/urandom', 'of=' + dummy_file, 'bs=16M',
          'count=6']) # TODO(vladum): count=64

    return dummy_file

if __name__ == '__main__':
    dummy_file = set_up_files()

    sipport = '127.0.0.1:10000'
    seeder = Seeder(sipport, '127.0.0.1:10001', dummy_file)
    
    seeder.start_process()
    seeder.set_maxspeed_upload(1024) # KiB/s

    roothash = seeder.get_roothash_blocking()
    print 'got roothash from seeder:', roothash
    
    leecher1 = Leecher(sipport, '127.0.0.2:20001', roothash, 'leecher1', 
        '20002')
    leecher1._cwd = os.path.abspath(os.path.join(TMPDIR, 'leecher1'))
    
    leecher2 = Leecher(sipport, '127.0.0.2:30001', roothash, 'leecher2', 
        '30002')
    leecher2._cwd = os.path.abspath(os.path.join(TMPDIR, 'leecher2'))
    
    #seeder.send_peer_weigths([
    #    ('127.0.0.1', 30002, 10), 
    #    ('127.0.0.1', 20002, 1)
    #])
    
    leecher1.start_process()
    #time.sleep(2)
    leecher2.start_process()

    def signal_handler(signal, frame):
        print 'Killing swifts...'
        leecher1.process.kill()
        leecher2.process.kill()
        seeder.process.kill()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    print 'Running for 230s... You can safely kill me with Ctrl+C...'
    time.sleep(230)

    leecher1.process.kill()
    leecher2.process.kill()
    seeder.process.kill()
