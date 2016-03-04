# -*- coding: utf-8 -*-

import socket as s

target_host = "127.0.0.1"
target_port = 9999

# make socket object
# SOCK_STREAM is using TCP
client = s.socket(s.AF_INET, s.SOCK_STREAM)


# connect to server
client.connect((target_host, target_port))

# send data in python3

client.send(b"GET / HTTP/1.1\r\nHost: hello\r\n\r\n")


# receive data
response = client.recv(4096)

print(response.decode())
