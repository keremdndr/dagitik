import threading
from Queue import Queue
from _socket import gethostname
from random import randint
from socket import socket, error
import ip
import time

THREADNUM = 5
CONNECT_POINT_LIST = []  # list array of [ip,port,type,time]


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
                else:  # not in cpl and not regme
                    self.sock_send("REGERR")
            else:  # regme
                conn_ip, port = request[5:].split(":")
                self.cpl_lock.acquire()
                for conn in CONNECT_POINT_LIST:
                    if conn_ip in conn and port in conn:
                        self.sock_send("REGOK")
                        conn[3] = time.time()
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
    def __init__(self, server_socket, host, port, server_conn_queue):
        super(ServerThread, self).__init__()
        self.sock = server_socket
        self.host = host
        self.port = port
        self.conn = None
        self.addr = None
        self.connection_list = {}
        self.queue = server_conn_queue
        self.threads = []

    def run(self):
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        while True:
            try:
                print "Server is waiting for new connection..."
                self.conn, self.addr = self.sock.accept()
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

    def check_server(self,addr):
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

    def run(self):
        try:
            pass
        except Exception, ex:
            print ex.message


def main():
    host = gethostname()
    server_socket = socket()
    port = randint(50000, 65000)
    threads = []
    server_queue = Queue(50)
    client_queue = Queue(50)
    cpl_lock = threading.Lock()
    try:
        for t in range(0, THREADNUM):
            thread = ServerWorkerThread(server_queue, cpl_lock, client_queue)
            thread.start()
            threads.append(thread)

        server_thread = ServerThread(server_socket, host, port, server_queue)
        server_thread.run()

        client_thread = ClientThread(client_queue, cpl_lock)
        client_thread.run()

    except Exception, ex:
        print ex.message
        return


if __name__ == '__main__':
    main()
