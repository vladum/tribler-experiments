import os
from socket import socket, AF_INET, SOCK_DGRAM

cmdgw_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

class LocalSwiftInstance():
    def __init__(self, listen, cmdgw):
        self.__cmdgw_sock = socket(AF_INET, SOCK_DGRAM)
        [self.__cmdgw_ip, self.__cmdgw_port] = cmdgw.split(':')
    
    def start_process():
        #set log pipes...
        #self.pid = ...
        pass
    
    def send_peer_weigths(weights):
        msg = ''.join([
            ip + ':' + str(port) + ':' + str(weight) 
            for (ip, port, weight) in weights
        ])
        self.__cmdgw_sock.sendto(
            'RECIPROCITY PEERWEIGHTS ' + msg,
            (self.__cmdgw_ip, int(self.__cmdgw_port)))

if __name__ == '__main__':
    leecher1 = LocalSwiftInstance('127.0.0.2:20000', '127.0.0.2:20001')
    leecher2 = LocalSwiftInstance('127.0.0.3:30000', '127.0.0.3:30001')    
    seeder = LocalSwiftInstance('127.0.0.1:10000', '127.0.0.1:10001')

    seeder.start_process()
    
