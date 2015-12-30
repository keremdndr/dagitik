import threading
from Queue import Queue
from _socket import gethostname
from socket import socket

import time

THREADNUM = 5
CONNECT_POINT_LIST = []  # list array of [ip,port,type,time]
SERVER_PORT = 12345
SERVER_HOST = gethostname()


class ServerThread(threading.Thread):
    def __init__(self, name, server_conn_queue):
        super(ServerThread, self).__init__()
        self.name = name
        self.conn = None
        self.conn_addr = None
        self.queue = server_conn_queue
        self.threads = []
        self.host = SERVER_HOST
        self.server_socket = socket()
        self.port = SERVER_PORT

    def run(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(10)

        while True:
            try:
                print "Server is waiting for new connection..."
                self.conn, self.conn_addr = self.server_socket.accept()
                print 'Got a connection from ', self.conn_addr
                self.queue.put((self.conn, self.conn_addr))
            except Exception, ex:
                print ex
                self.server_socket.close()
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
            print ex

    def parser(self, request):
        request = request.strip()
        if len(request) >= 5:
            if request[0:5] == "HELLO":  # hello request doesn't need registration.
                self.sock_send("SALUT N")
            elif not request[0:5] == "REGME":  # if the protocol is not register, check the cpl
                for conn in CONNECT_POINT_LIST:
                    if self.connection[1][0] in conn:  # if connection's ip address is in cpl
                        if request[0:5] == "CLOSE":
                            self.sock_send("BUBYE")
                        elif request[0:5] == "GETNL":
                            nlsize = len(CONNECT_POINT_LIST)
                            i = 0
                            if len(request) > 5:
                                nlsize = int(request[6:])
                            self.sock_send("NLIST BEGIN\n")
                            for conn2 in CONNECT_POINT_LIST:
                                self.sock_send(conn2[0] + ":" +
                                               str(conn2[1]) + ":" +
                                               conn2[2] + ":" +
                                               str(conn2[3]) + "\n")
                                i += 1
                                if i == nlsize:
                                    break
                            self.sock_send("NLIST END")
                        else:
                            self.sock_send("CMDERR")
                            pass
                        break
                else:  # not in cpl and not regme
                    self.sock_send("REGERR")
            else:  # regme
                conn_ip, port = request[6:].split(":")
                self.cpl_lock.acquire()
                for conn in CONNECT_POINT_LIST:
                    if conn_ip in conn and int(port) in conn:
                        self.sock_send("REGOK")
                        conn[3] = time.time()
                        break
                else:
                    self.sock_send("REGWA")
                    addr = (conn_ip, int(port))
                    self.client_queue.put((addr, "HELLO"))
                self.cpl_lock.release()
        else:
            self.sock_send("CMDER")

    def run(self):
        while True:
            try:
                if self.inqueue.qsize() > 0:
                    self.connection = self.inqueue.get()
                    request = ""
                    while request != "CLOSE":
                        request = self.connection[0].recv(1024)
                        request = request.strip()
                        self.parser(request)
                    self.connection[0].close()
            except Exception, ex:
                print ex
                return


class ClientThread(threading.Thread):
    def __init__(self, name, client_queue, cpl_lock):
        super(ClientThread, self).__init__()
        self.name = name
        self.cpl_lock = cpl_lock
        self.client_queue = client_queue

    def conn_sock(self, addr):
        s = socket()
        s.connect(addr)
        return s

    def check_server(self, addr):
        try:
            s = self.conn_sock(addr)
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
        except Exception, ex:
            print ex

    def close_conn(self, addr):
        try:
            s = self.conn_sock(addr)
            s.sendall("CLOSE")
            ans = s.recv(1024)
            ans = ans.strip()
            if ans[:5] == "BUBYE":
                s.close()
            else:
                s.sendall("CMDERR")
        except Exception, ex:
            print ex

    def run(self):
        try:
            while True:
                if self.client_queue.qsize() > 0:
                    request = self.client_queue.get()
                    addr = request[0]
                    mess = request[1]
                    if mess == "HELLO":
                        self.check_server(addr)
                    elif mess == None:
                        pass
                    else:
                        pass
        except Exception, ex:
            print ex


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

        server_thread = ServerThread("Server Thread", server_queue)
        server_thread.daemon = True
        server_thread.start()
        threads.append(server_thread)

        client_thread = ClientThread("Client Thread", client_queue, cpl_lock)
        client_thread.daemon = True
        client_thread.start()
        threads.append(client_thread)

        for t in threads:
            t.join()
    except Exception, ex:
        print ex


if __name__ == '__main__':
    main()
