import threading
from _socket import gethostname
from random import randint
from socket import socket
from twisted.python.util import println


class ServerThread(threading.Thread):
    def __init__(self, server_socket):
        super(ServerThread, self).__init__()
        self.sock = server_socket
        print "Server is waiting for new connection..."

    def parser(self, request):
        request = request.strip()
        if len(request) > 5:
            if request[0:5] == "HELLO":
                # doldurulacak
                pass
            elif request[0:5] == "CLOSE":
                # doldurulacak
                pass
            elif request[0:5] == "REGME":
                # doldurulacak
                pass
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
                data = self.sock.recv(1024)
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
        server_socket.bind((host, port))
        server_socket.listen(5)

        server_thread = ServerThread(server_socket)
        server_thread.run()

        client_thread = ClientThread()
        client_thread.run()


    except Exception, ex:
        print ex.message



if __name__ == '__main__':
    main()
