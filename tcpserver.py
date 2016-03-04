# -*- coding: utf-8 -*-

import socket as s
import threading

bind_ip = "0.0.0.0"
bind_port = 9999

server = s.socket(s.AF_INET, s.SOCK_STREAM)
server.bind((bind_ip, bind_port))

server.listen(5)

print("[*] Listening on {!s}:{:d}".format(bind_ip, bind_port))


#クライアント からの接続を処理するスレッド    
def handle_client(client_socket):
    req = client_socket.recv(1024).decode()
    print("[*] Received: {!s}".format(req))
    client_socket.send(b"ACK!")
    client_socket.close()


    
if __name__ == '__main__':
    while True:
        client, addr = server.accept()

        print("[*] Accepted connection from: {!s}:{:d}".format(addr[0], addr[1]))
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()







        
