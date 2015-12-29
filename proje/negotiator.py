import threading
from Queue import Queue
from _socket import gethostname
from socket import socket

import time

THREADNUM = 5
CONNECT_POINT_LIST = []  # list array of [ip,port,type,time]


class ServerThread(threading.Thread):
    def __init__(self, server_conn_queue):
        super(ServerThread, self).__init__()
        self.conn = None
        self.conn_addr = None
        self.connection_list = {}
        self.queue = server_conn_queue
        self.threads = []
        self.host = gethostname()
        self.server_socket = socket()
        self.port = 12345

    def run(self):
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        while True:
            try:
                print "Server is waiting for new connection..."
                self.conn, self.conn_addr = self.sock.accept()
                print 'Got a connection from ', self.addr
                self.queue.put((self.conn, self.addr))
            except Exception, ex:
                print ex.message
                return


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
                self.sock_send("SALUT N")
            elif not request[0:5] == "REGME":  # if the protocol is not register, check the cpl
                for conn in CONNECT_POINT_LIST:
                    if self.connection[1][0] in conn:  # if connection's ip address is in cpl
                        if request[0:5] == "CLOSE":
                            self.sock_send("BUBYE")
                        else:
                            self.sock_send("CMDERR")
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


def main():
    threads = []
    server_queue = Queue(50)
    client_queue = Queue(50)
    cpl_lock = threading.Lock()
    try:
        for t in range(0, THREADNUM):
            thread = ServerWorkerThread(server_queue, cpl_lock, client_queue)
            thread.daemon = True
            thread.start()
            threads.append(thread)

        server_thread = ServerThread(server_queue)
        server_thread.daemon = True
        server_thread.run()
        threads.append(server_thread)

        client_thread = ClientThread(client_queue, cpl_lock)
        client_thread.daemon = True
        client_thread.run()
        threads.append(client_thread)

        for t in threads:
            t.join()
    except Exception, ex:
        print ex.message
        return


if __name__ == '__main__':
    main()
