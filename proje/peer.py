import threading
from _socket import gethostname
from random import randint
from socket import socket
import time


class ServerThread(threading.Thread):
    def __init__(self, server_socket, host, port):
        super(ServerThread, self).__init__()
        self.sock = server_socket
        self.host = host
        self.port = port
        self.conn = None
        self.addr = None
        self.connection_list = {}

    def parser(self, request):
        request = request.strip()
        answer = ""
        if len(request) > 5:
            if request[0:5] == "HELLO":
                answer = "SALUT  P"
            elif request[0:5] == "CLOSE":
                answer = "BUBYE"
            elif request[0:5] == "REGME":
                ip, port = request[5:].split(":")

            elif request[0:5] == "GETNL":
                # doldurulacak
                pass
            elif request[0:5] == "FUNLS":
                # doldurulacak
                pass
            elif request[0:5] == "FUNRQ":
                # doldurulacak
                pass
            elif request[0:5] == "EXERQ":
                # doldurulacak
                pass
            elif request[0:5] == "PATCH":
                # doldurulacak
                pass
            else:
                # cmderr
                pass
        else:
            # cmderr
            pass

    def run(self):
        while True:
            try:
                self.sock.bind((self.host, self.port))
                self.sock.listen(5)
                print "Server is waiting for new connection..."
                self.conn, self.addr = self.sock.accept()
                print 'Got a connection from ', self.addr
                data = self.conn.recv(1024)
                self.parser(data)
            except Exception, ex:
                print ex.message


class ClientThread(threading.Thread):
    def __init__(self):
        super(ClientThread, self).__init__()

    def requester(self):
        pass


def main():
    host = gethostname()
    server_socket = socket()
    port = randint(50000, 65000)
    try:

        server_thread = ServerThread(server_socket, host, port)
        server_thread.run()

        client_thread = ClientThread()
        client_thread.run()


    except Exception, ex:
        print ex.message



if __name__ == '__main__':
    main()
