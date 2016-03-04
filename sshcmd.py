#!/Users/kawasakitaku/Documents/python-PVM/basic_test_3/bin/python
# -*- coding: utf-8 -*-

import threading
import paramiko
import subprocess

def ssh_command(ip,user,passwd,command):
    client = paramiko.SSHClient()
    client.load_host_keys('/home/user/.ssh/known_hosts')
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    
    client.connect(ip,username = user, password = passwd)

    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.exec_command(command)
        print(str(ssh_session.recv(1024),'utf-8'))
    return


ssh_command('ip','','','ls -al')
