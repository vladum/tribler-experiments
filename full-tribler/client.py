import xmlrpclib

s = xmlrpclib.ServerProxy('http://localhost:8000')

print s.leech('tswift://123.123.123.123:12/deadbeef12deadbeef12deadbeef12deadbeef12')
