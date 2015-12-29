import threading
from Queue import Queue
from _socket import gethostname
from random import randint
from socket import socket, error
import ip
import time

THREADNUM = 5
CONNECT_POINT_LIST = []  # list array of [ip,port,type,time]
FUNCTION_LIST = ["grayscale","binarize","sobelfilter","gaussianfilter","prewittfilter"]
SERVER_HOST = gethostname()
SERVER_PORT = randint(50000,65000)

class ServerWorkerThread(threading.Thread):
    def __init__(self, inqueue, cpl_lock, client_queue):
        super(ServerWorkerThread, self).__init__()
        self.client_queue = client_queue
        self.cpl_lock = cpl_lock
        self.inqueue = inqueue
        self.connection = None

    def sock_send(self, data):
        try:
            self.connection[0].sendall(data)
        except Exception, ex:
            print ex.message

    def parser(self, request):
        request = request.strip()

        if len(request) > 5:
            if request[0:5] == "HELLO":  # hello request doesn't need registration.
                self.sock_send("SALUT P")
            elif not request[0:5] == "REGME":  # if the protocol is not register, check the cpl
                for conn in CONNECT_POINT_LIST:
                    if self.connection[1][0] in conn:  # if connection's ip address is in cpl
                        if request[0:5] == "CLOSE":
                            self.sock_send("BUBYE")
                        elif request[0:5] == "GETNL":
                            nlsize = len(CONNECT_POINT_LIST)
                            i = 1
                            if len(request) > 5:
                                nlsize = int(request[5:])
                            self.sock_send("NLIST BEGIN\n")
                            for conn2 in CONNECT_POINT_LIST:
                                self.sock_send(conn2[0] + ":" +
                                               conn2[1] + ":" +
                                               conn2[2] + ":" +
                                               conn2[3] + "\n")
                                i += 1
                                if i == nlsize:
                                    break
                            self.sock_send("NLIST END")
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
                        break
                else:  # not in cpl and not regme
                    self.sock_send("REGERR")
            else:  # regme
                conn_ip, port = request[5:].split(":")
                self.cpl_lock.acquire()
                for conn in CONNECT_POINT_LIST:
                    if conn_ip in conn and port in conn:
                        self.sock_send("REGOK")
                        conn[3] = time.time()
                        break
                else:
                    self.sock_send("REGWA")
                    addr = (conn_ip, port)
                    self.client_queue.put((addr, "HELLO"))
                self.cpl_lock.release()
        else:
            self.sock_send("CMDER")

    def run(self):
        while True:
            try:
                if self.inqueue.qsize() > 0:
                    request = ""
                    self.connection = self.inqueue.get()
                    message_length = int(self.connection[0].recv(100))
                    while len(request) < message_length:
                        request += self.connection[0].recv(1024)
                    self.parser(request)
            except Exception, ex:
                print ex.message
                return


class ServerThread(threading.Thread):
    def __init__(self, server_conn_queue):
        super(ServerThread, self).__init__()
        self.conn = None
        self.conn_addr = None
        self.queue = server_conn_queue
        self.threads = []
        self.host = SERVER_HOST
        self.server_socket = socket()
        self.port = SERVER_PORT

    def run(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        while True:
            try:
                print "Server is waiting for new connection..."
                self.conn, self.conn_addr = self.sock.accept()
                print 'Got a connection from ', self.addr
                self.queue.put((self.conn, self.addr))
            except Exception, ex:
                print ex.message
                return


class ClientThread(threading.Thread):
    def __init__(self, client_queue, cpl_lock):
        super(ClientThread, self).__init__()
        self.cpl_lock = cpl_lock
        self.client_queue = client_queue
        self.timer = threading.Timer(1.0, self.check_request())
        self.timer.start()

    def requester(self):
        pass

    def conn_sock(self, addr):
        s = socket()
        s.connect(addr)
        return s

    def check_server(self, addr):
        try:
            s = socket()
            s.connect(addr)
            s.sendall("HELLO")
            ans = s.recv(1024)
            ans = ans.strip()
            if ans == "SALUT P" or ans == "SALUT N":
                self.cpl_lock.acquire()
                for conn in CONNECT_POINT_LIST:
                    if addr[0] in conn and addr[1] in conn:
                        conn[3] = time.time()
                        break
                else:
                    CONNECT_POINT_LIST.append([addr[0], addr[1], ans[6], time.time()])
                self.cpl_lock.release()
            else:
                s.sendall("CMDERR")
        except error, err:
            print err.message

    def check_request(self):
        if self.client_queue.qsize() > 0:
            request = self.client_queue.get()
            addr = request[0]
            mess = request[1]
            if mess == "HELLO":
                self.check_server(addr)
            else:
                pass  # doldurulacak

    def update(self):
        self.cpl_lock.acquire()
        for conn in CONNECT_POINT_LIST:
            if conn[2] == "N":
                s = self.conn_sock((conn[0],conn[1]))
                s.sendall("GETNL")
                break
    def run(self):
        try:
            pass
        except Exception, ex:
            print ex.message


def main():
    threads = []
    server_queue = Queue(50)
    client_queue = Queue(50)
    cpl_lock = threading.Lock()
    try:
        for t in range(0, THREADNUM):
            thread = ServerWorkerThread(server_queue, cpl_lock, client_queue)
            thread.start()
            threads.append(thread)

        server_thread = ServerThread(server_queue)
        server_thread.run()

        client_thread = ClientThread(client_queue, cpl_lock)
        client_thread.run()

    except Exception, ex:
        print ex.message
        return


if __name__ == '__main__':
    main()
