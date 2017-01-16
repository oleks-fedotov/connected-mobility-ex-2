#!/usr/bin/env python3
import socket
from binascii import hexlify, unhexlify

HOST1 = '10.0.0.3'
HOST2 = '10.1.0.3'
PORT = 80

print("attempting connection")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("socket started")

try:
    print("attempt connection on host 1")
    s.connect((HOST1, PORT))

except socket.error as msg:
    print("attempt connection on host 2")
    s.connect((HOST2, PORT))

sf = s.makefile("rw")  # we use a file abstraction for the sockets


data = sf.readline().rstrip('\n')
#print("From Server: `{}'".format(data))

#data = sf.readline().rstrip('\n')
#print("From Server: received {} bytes".format(len(data)))

data = unhexlify(data)

#pdf_hdr = b'%PDF-1.5'

#if len(data) >= len(pdf_hdr) and data[:len(pdf_hdr)] == pdf_hdr:
#    print("Looks like we got a PDF!")

print("looks like we got a file!")

with open('somestuff.html', 'wb') as fo:
    fo.write(data)

print("file successfully saved, closing sockets")

sf.close()
s.close()

s.close()
