import os
import socket

def get_nodes():
    return os.environ['HOSTS'].strip().split(' ')

def get_current_node():
    # os.environ['HOSTNAME'] is not reliable (multiple hosts with the same val)
    return socket.gethostname()

def get_current_node_ip():
    return socket.gethostbyname(get_current_node())

def get_node_ips():
    return map(lambda h: socket.gethostbyname(h), get_nodes())

def get_master_node():
    # remove "node" part from nodeXXX and convert remaining to id
    # the node with the smallest id is the master
    return min(get_nodes(), key=lambda n: int(n[4:]))

def get_master_node_ip():
    return socket.gethostbyname(get_master_node())

def get_nodes_no():
    return int(os.environ['NHOSTS'].strip())

