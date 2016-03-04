#!/Users/kawasakitaku/Documents/python-PVM/basic_test_2.7/bin/python
# -*- coding: utf-8 -*-

import socket as s
import paramiko
import threading
import sys


host_key = paramiko.RSAKey.from_private_key_file(
    filename='/home/user/.ssh/id_rsa.pub')


class Server(paramiko.ServerInterface):
    
    def __init__(self):
        self.event = threading.Event()
        
    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if username == '' and password == '':
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

server = sys.argv[1]
ssh_port = int(sys.argv[2])

try:
    sock = s.socket(s.AF_INET, s.SOCK_STREAM)
    s.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
    sock.bind((server, ssh_port))
    sock.listen(100)
    print("[+] Listening for connection... ")
    client, addr = sock.accept()

except Exception as e:
    print("[-]  Listen failed: " + str(e))
    sys.exit(1)
print("[+] got a connection")

try:
    Session = paramiko.Transport(client)
    Session.add_server_key(host_key)
    server = Server()
    try:
        Session.start_server(server=server)
    except paramiko.SSHException as x:
        print("[-] SSH negotiation failed.")

    chan = Session.accept(20)
    print("[+] Authenticated!")
    print(chan.recv[1024])

    chan.send("Welcome to ssh!!!")

    while True:
        try:
            command = input("Enter command: ").strip('\n')
            if command != 'exit':
                chan.send(command)
                print(chan.recv(1024) + '\n')
            else:
                chan.send('exit')
                print('exiting')
                Session.close()
                raise Exception("exit")
        except KeyboardInterrupt:
            Session.close()
except Exception as e:
    print("[-] caught exception: " + str(e))
    try:
        Session.close()
    except:
        pass
    sys.exit(1)
