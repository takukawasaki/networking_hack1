#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import socket as s
import sys
import threading

def server_loop(local_host,
                local_port,
                remote_host,
                remote_port,
                receive_first):

    server = s.socket(s.AF_INET, s.SOCK_STREAM)

    try:
        server.bind((local_host,local_port))
    except:
        print("[!!] Failed to listen on {!s}:{:d}".format(local_host,local_port))
        print("[!!] Check for other listening socket or correct permisssions. ")

        sys.exit(0)

    print("[*] Listening on {!s}:{:d}".format(local_host,local_port))

    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        print("[==>] Received incomming connection from {!s}:{:d}".format(addr[0],addr[1]))
        proxy_thread = threading.Thread(target = proxy_handler,
                                        args   = (client_socket,
                                                    remote_host,
                                                    remote_port,
                                                    receive_first),)

        proxy_thread.start()



def main():
    if len(sys.argv[1:]) != 5:
        print("Usage: ./bhproxy.py [localhost] [localport] [remotehost] [remoteport] [receive_first]")
        print("Example: ./bhproxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)

    local_host = sys.argv[1] #local hostname
    local_port = int(sys.argv[2]) #port number

    remote_host = sys.argv[3] #remote hostname
    remote_port = int(sys.argv[4]) #port number

    receive_first = sys.argv[5]

    
    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False

    try:
        server_loop(local_host,local_port, remote_host,remote_port, receive_first)
    except KeyboardInterrupt as e:
        print("\nProxy Server close")

    
def proxy_handler(client_socket,
                    remote_host,
                    remote_port,
                    receive_first):
    
    #connect to remote host
    remote_socket = s.socket(s.AF_INET,s.SOCK_STREAM)
    remote_socket.connect((remote_host,remote_port))

    # receive data from remote host
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

        #受信データ処理関数にデータ受け渡し
        remote_buffer = bytes(response_handler(remote_buffer),'utf-8')

        #ローカル側に送るデータがあれば送信
        if len(remote_buffer):
            print("[<==] Sending {:d} bytes to localhost".format(len(remote_buffer)))
            client_socket.send(remote_buffer)

    #ローカルからのデータ受信、リモートへの送信、ローカルへの送信
    #の繰り返しを行うループ処理
    while True:
        #data from localhost
        local_buffer = receive_from(client_socket) #receive string

        if len(local_buffer):
            print("[==>] Received {:d} bytes from localhost".format(len(local_buffer)))
            hexdump(local_buffer)

            #送信データ処理関数にデータ受け渡し
            local_buffer = bytes(request_handler(local_buffer),'utf-8')

            remote_socket.send(local_buffer)
            print("[==>] Sent to remote")

        #応答の受信
        remote_buffer = receive_from(remote_socket)
        
        if len(remote_buffer):
            print("[<==] Received {:d} bytes from remote .".format(len(remote_buffer)))
            hexdump(remote_buffer)

            #受信データ処理関数にデータ受け渡し
            remote_buffer = bytes(response_handler(remote_buffer),'utf-8')

            #ローカル側に応答データ送信
            client_socket.send(remote_buffer)

            print("[<==] Sent to localhost")

        #local remote ともにデータがなければ接続を閉じる
        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closeing connections.")

            break

def hexdump(src, length=16):
    result = []
    digits = 2 if isinstance(src,bytes) else 4
    for i in range(0,len(src), length):
        s=src[i:i+length]
        hexa = ' '.join(["%0*X" % (digits, ord(x)) for x in s])
        text = ''.join([x if 0x20 <= ord(x) < 0x7F else '.' for x in s])
        result.append('%04X   %-*s   %s' % (i, length*(digits + 1),hexa,text))
    print('\n'.join(result))

        
def receive_from(connection):
    buffer = ''
    connection.settimeout(5)    
    try:
        while True:
            data = str(connection.recv(4096),'utf-8')
            if not data:
                break
            buffer += data
    except:
        pass
    return buffer

def request_handler(buffer):
    return buffer


def response_handler(buffer):
    return buffer


if __name__ == '__main__':
    main()
            
            
            
            
    





    
        
        
        
    
