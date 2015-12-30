import threading
from Queue import Queue
from _socket import gethostname
from random import randint
from socket import socket, error
import ip
import time

THREADNUM = 3
CONNECT_POINT_LIST = [[gethostname(), 12345, "N", time.time()]]  # list array of [ip,port,type,time]
#  initialised with known nego
FUNCTION_LIST = ["grayscale", "binarize:threshold", "sobelfilter:threshold", "prewittfilter:threshold"]
SERVER_HOST = gethostname()
SERVER_PORT = randint(50000, 65000)


class ServerWorkerThread(threading.Thread):
    def __init__(self, name, inqueue, cpl_lock, client_queue):
        super(ServerWorkerThread, self).__init__(name=name)
        self.client_queue = client_queue
        self.cpl_lock = cpl_lock
        self.inqueue = inqueue
        self.connection = None

    def parser(self, request):
        request = request.strip()
        if len(request) >= 5:
            if request[0:5] == "HELLO":  # hello request doesn't need registration.
                data = "SALUT P"
                self.connection[0].sendall(data)
            elif not request[0:5] == "REGME":  # if the protocol is not register, check the cpl
                for conn in CONNECT_POINT_LIST:
                    if self.connection[1][0] in conn:  # if connection's ip address is in cpl
                        if request[0:5] == "CLOSE":
                            data = "BUBYE"
                            self.connection[0].sendall(data)
                        elif request[0:5] == "GETNL":
                            nlsize = len(CONNECT_POINT_LIST)
                            i = 0
                            if len(request) > 5:
                                nlsize = int(request[6:])
                            data = "NLIST BEGIN\n"
                            self.connection[0].sendall(data)
                            for conn2 in CONNECT_POINT_LIST:
                                data = conn2[0] + ":" \
                                       + str(conn2[1]) + ":" \
                                       + conn2[2] + ":" \
                                       + str(conn2[3]) + "\n"
                                self.connection[0].sendall(data)
                                i += 1
                                if i == nlsize:
                                    break
                            data = "NLIST END"
                            self.connection[0].sendall(data)
                        elif request[0:5] == "FUNLS":
                            data = "FUNLI BEGIN\n"
                            self.connection[0].sendall(data)
                            for f in FUNCTION_LIST:
                                data = f+"\n"
                                self.connection[0].sendall(data)
                            data = "FUNLI END"
                            self.connection[0].sendall(data)
                        elif request[0:5] == "FUNRQ":
                            func_name = request[6:]
                            for f in FUNCTION_LIST:
                                name, param = f.split(":")
                                if name == func_name:
                                    data = "FUNYS "+f
                                    self.connection[0].sendall(data)
                                    break
                            else:
                                data = "FUNNO "+func_name
                                self.connection[0].sendall(data)
                        elif request[0:5] == "EXERQ":
                            pass
                        elif request[0:5] == "PATCH":
                            pass
                        else:
                            data = "CMDERR"
                            self.connection[0].sendall(data)
                            pass
                        break
                else:  # not in cpl and not regme
                    data = "REGER"
                    self.connection[0].sendall(data)
            else:  # regme
                conn_ip, port = request[6:].split(":")
                self.cpl_lock.acquire()
                for conn in CONNECT_POINT_LIST:
                    if conn_ip in conn and int(port) in conn:
                        data = "REGOK"
                        self.connection[0].sendall(data)
                        conn[3] = time.time()
                        break
                else:
                    data = "REGWA"
                    self.connection[0].sendall(data)
                    addr = (conn_ip, int(port))
                    self.client_queue.put((addr, "HELLO"))
                self.cpl_lock.release()
        else:
            data = "CMDER"
            self.connection[0].sendall(data)

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
                print self.name, ex, "run"


class ServerThread(threading.Thread):
    def __init__(self, name, server_conn_queue):
        super(ServerThread, self).__init__(name=name)
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
                self.conn, self.conn_addr = self.server_socket.accept()
                print 'Got a connection from ', self.conn_addr
                self.queue.put((self.conn, self.conn_addr))
            except Exception, ex:
                print self.name, ex


class ClientThread(threading.Thread):
    def __init__(self, name, client_queue, cpl_lock):
        super(ClientThread, self).__init__(name=name)
        self.cpl_lock = cpl_lock
        self.client_queue = client_queue
        self.utimer = threading.Timer(600.0, self.update())
        self.utimer.start()

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
        except error, err:
            print self.name, err

    def update(self):
        self.cpl_lock.acquire()
        for conn in CONNECT_POINT_LIST:
            if conn[2] == "N":
                s = self.conn_sock((conn[0], conn[1]))
                s.sendall("GETNL")
                rec = s.recv(100)
                rec.strip()
                if rec == "REGER":
                    s.sendall("REGME " + str(SERVER_HOST) + ":" + str(SERVER_PORT))
                    ans = s.recv(100)
                    if ans.strip() == "REGWA":
                        time.sleep(3)
                        s.sendall("REGME " + str(SERVER_HOST) + ":" + str(SERVER_PORT))
                        ans = s.recv(100)
                    if ans.strip() == "REGOK":
                        s.sendall("GETNL")
                        rec = s.recv(100)
                        rec.strip()
                if rec == "NLIST BEGIN":
                    while rec != "NLIST END":
                        rec = s.recv(200)
                        rec.strip()
                        conn_point = rec.split(":")
                        conn_point[2] = int(conn_point[1])
                        conn_point[3] = float(conn_point[3])
                        for conn2 in CONNECT_POINT_LIST:
                            if conn_point[0] in conn2 and conn_point[1] in conn2:
                                if conn_point[3] > conn2[3]:
                                    conn2[3] = conn_point[3]
                        else:
                            CONNECT_POINT_LIST.append(conn_point)

    def conn_system(self):
        s = socket()
        s.connect((gethostname(), 12345))
        s.sendall("REGME " + str(SERVER_HOST) + ":" + str(SERVER_PORT))
        ans = s.recv(100)
        if ans.strip() == "REGWA":
            time.sleep(3)
            s.sendall("REGME " + str(SERVER_HOST) + ":" + str(SERVER_PORT))
            ans = s.recv(100)
        if ans.strip() == "REGOK":
            return True
        else:
            return False

    def run(self):
        try:
            if self.conn_system():
                print "Connected to first negotiator." \
                      "Now will try to update NLIST"
                self.update()
            else:
                print "Could't connected to first Negotiator, please try again later."
            while True:
                if self.client_queue.qsize() > 0:
                    request = self.client_queue.get()
                    addr = request[0]
                    mess = request[1]
                    if mess == "HELLO":
                        self.check_server(addr)
                    else:
                        pass  # doldurulacak
        except Exception, ex:
            print self.name, ex


def main():
    threads = []
    server_queue = Queue(50)
    client_queue = Queue(50)
    cpl_lock = threading.Lock()
    # ip class variables
    thread_number = 3
    max_size = thread_number * 25
    worker_threads = []
    worker_queue = Queue()
    processed_queue = Queue(max_size)
    process_lock = threading.Lock()
    try:
        for t in range(0, THREADNUM):
            thread = ServerWorkerThread("Server Worker Thread "+str(t), server_queue, cpl_lock, client_queue)
            thread.start()
            threads.append(thread)

        server_thread = ServerThread("Main server thread", server_queue)
        server_thread.start()
        threads.append(server_thread)

        client_thread = ClientThread("Maine Client Thread", client_queue, cpl_lock)
        client_thread.start()
        threads.append(client_thread)

        # ip class threads and app begin
        for i in range(0, thread_number):
            w_thread = ip.WorkerThread("Worker Thread "+str(i), worker_queue, processed_queue, process_lock)
            w_thread.start()
            worker_threads.append(w_thread)

#        app = ip.ImGui(worker_queue, processed_queue, process_lock)
#        app.run()
        for t in threads:
            t.join()
    except Exception, ex:
        print __name__, ex
        return


if __name__ == '__main__':
    main()
