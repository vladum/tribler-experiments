import os
import shlex
import time
from socket import socket, AF_INET, SOCK_STREAM
from subprocess import call, Popen
from threading import Thread

TMPDIR = './tmp'
LOGSDIR = os.path.join(TMPDIR, 'logs')
PLOTDIR = os.path.join(TMPDIR, 'plots')
SWIFTBINARY = './swift'

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
            '-u', '1024', #uprate
            #'-m',
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
        msg = 'RECIPROCITY PEERWEIGHTS ' + msg + '\r\n'
        print 'sending:', msg, 'to:', (self.__cmdgw_ip, int(self.__cmdgw_port))
        self.__cmdgw_sock.send(msg)
        
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
            #'-B',
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
    silent_mkdir(os.path.join(TMPDIR, 'leecher2'))
    silent_mkdir(LOGSDIR)
    silent_mkdir(os.path.join(LOGSDIR, 'seeder'))
    silent_mkdir(os.path.join(LOGSDIR, 'leecher1'))
    silent_mkdir(os.path.join(LOGSDIR, 'leecher2'))
    silent_mkdir(PLOTDIR)

    dummy_file = os.path.join(TMPDIR, 'seeder', 'somefile')
    # 1GiB file
    call(['dd', 'if=/dev/urandom', 'of=' + dummy_file, 'bs=16M',
          'count=3']) # TODO(vladum): count=64

    return dummy_file

def plog_stderr(filename, plotfile, starttime, isseeder=False):
    pf = open(plotfile, 'w')
    f = open(filename, 'r')
    stop = False
    while True:
        line = f.readline()
        if line == '':
            print 'swift process might be dead'
            break
        if line.startswith('done') or line.startswith('DONE'):
            if line.startswith('DONE') and not isseeder:
                stop = True
            progress = line.split(' ')[1]
        elif line.startswith('upload'):
            upload = line.split(' ')[1][:-1].split('.')[0]
        elif line.startswith('dwload'):
            dwload = line.split(' ')[1][:-1].split('.')[0]
            print >>pf, str(int(time.time() - starttime)), progress, upload, dwload
            pf.flush()
        if isseeder:
            print line[:-1]

        if stop:
            break
    f.close()
    pf.close()
    print 'peer finished! plog in file:', plotfile

if __name__ == '__main__':
    dummy_file = set_up_files()

    sipport = '127.0.0.1:10000'
    seeder = Seeder(sipport, '127.0.0.1:10001', dummy_file)
    pfseeder = os.path.join(PLOTDIR, 'seeder.plog')
    os.mkfifo(seeder._stderr)
    
    starttime = time.time()
    s = Thread(target=plog_stderr, args=(seeder._stderr, pfseeder, starttime, True))
    s.start()
    
    seeder.start_process()
    #seeder.send_start()
    roothash = seeder.get_roothash_blocking()
    print 'got roothash from seeder:', roothash
    
    leecher1 = Leecher(sipport, '127.0.0.2:20001', roothash, 'leecher1', '20002')
    leecher1._cwd = os.path.abspath(os.path.join(TMPDIR, 'leecher1'))
    pfleecher1 = os.path.join(PLOTDIR, 'leecher1.plog')
    os.mkfifo(leecher1._stderr)
    
    leecher2 = Leecher(sipport, '127.0.0.2:30001', roothash, 'leecher2', '30002')
    leecher2._cwd = os.path.abspath(os.path.join(TMPDIR, 'leecher2'))
    pfleecher2 = os.path.join(PLOTDIR, 'leecher2.plog')
    os.mkfifo(leecher2._stderr)
    
    t1 = Thread(target=plog_stderr, args=(leecher1._stderr, pfleecher1, starttime))
    t2 = Thread(target=plog_stderr, args=(leecher2._stderr, pfleecher2, starttime))
    t1.start()
    t2.start()
    
    #seeder.send_peer_weigths([('127.0.0.1', 30002, 10), ('127.0.0.1', 20002, 1)])
    
    leecher1.start_process()
    leecher2.start_process()

    t1.join()
    t2.join()
    
    leecher1.process.kill()
    leecher2.process.kill()
    seeder.process.kill()
