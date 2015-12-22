import threading
from socket import socket


class ServerThread(threading.Thread):
    def __init__(self):
        super(ServerThread, self).__init__()

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
        pass


class ClientThread(threading.Thread):
    def __init__(self):
        super(ClientThread, self).__init__()

    def requester(self):
        pass


def main():
    pass


if __name__ == '__main__':
    main()
