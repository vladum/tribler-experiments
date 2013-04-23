import os
import shlex
from socket import socket, AF_INET, SOCK_DGRAM
from subprocess import call, Popen

TMPDIR = './tmp'
LOGSDIR = os.path.join(TMPDIR, 'logs')
SWIFTBINARY = './swift'

class LocalSwiftInstance():
    def __init__(self, listen, cmdgw, filename):
        self.name = 'seeder'
        self.listen = listen
        self.filename = filename
        self.__cwd = None
        self.__cmdgw_sock = socket(AF_INET, SOCK_DGRAM)
        [self.__cmdgw_ip, self.__cmdgw_port] = cmdgw.split(':')
        self.__dir = os.path.join(TMPDIR, self.name)
        self.__stderr = os.path.join(LOGSDIR, self.name, 'stderr.log')
        self.__stdout = os.path.join(LOGSDIR, self.name, 'stdout.log')
    
    def start_process(self):
        cmd = [
            SWIFTBINARY, 
            '-l', self.listen, 
            '-p', 
            '-n', self.__dir, 
            '-f', self.filename,
            '-B'
        ]
        print 'launching:', ''.join(cmd)
        fstdout = open(self.__stdout, 'w')
        fstderr = open(self.__stderr, 'w')
        self.process = Popen(
            args=cmd,
            stdout=fstdout,
            stderr=fstderr,
            cwd=self.__cwd
        )
        print 'process started: name =', self.name,
        print ' pid =', self.process.pid
    
    def send_peer_weigths(self, weights):
        msg = ''.join([
            ip + ':' + str(port) + ':' + str(weight) 
            for (ip, port, weight) in weights
        ])
        self.__cmdgw_sock.sendto(
            'RECIPROCITY PEERWEIGHTS ' + msg,
            (self.__cmdgw_ip, int(self.__cmdgw_port)))

def set_up_files():
    try:
        os.mkdir(TMPDIR)
        os.mkdir(os.path.join(TMPDIR, 'seeder'))
        os.mkdir(LOGSDIR)
        os.mkdir(os.path.join(LOGSDIR, 'seeder'))
    except OSError as _:
        # Do nothing if already exists.
        pass
    dummy_file = os.path.join(TMPDIR, 'seeder', 'somefile')
    # 1GiB file
    call(['dd', 'if=/dev/urandom', 'of=' + dummy_file, 'bs=16M',
          'count=1']) # TODO(vladum): count=64
    return dummy_file

if __name__ == '__main__':
    dummy_file = set_up_files()

    seeder = LocalSwiftInstance(
        '127.0.0.1:10000',
        '127.0.0.1:10001',
        dummy_file
    )
    seeder.start_process()
    
    # TODO(vladum): Get roothash from stdout.
    
    #leecher1 = LocalSwiftInstance('127.0.0.2:20000', '127.0.0.2:20001', seeder.roothash)
    #leecher2 = LocalSwiftInstance('127.0.0.3:30000', '127.0.0.3:30001', seeder.roothash)    

