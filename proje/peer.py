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

    def sock_send(self, data):
        try:
            self.connection[0].sendall(data)
        except Exception, ex:
            print self.name, ex, "sock_send"

    def parser(self, request):
        request = request.strip()
        if len(request) >= 5:
            if request[0:5] == "HELLO":  # hello request doesn't need registration.
                self.sock_send("SALUT P")
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
                        elif request[0:5] == "FUNLS":
                            self.sock_send("FUNLI BEGIN\n")
                            for f in FUNCTION_LIST:
                                self.sock_send(f+"\n")
                            self.sock_send("FUNLI END")
                        elif request[0:5] == "FUNRQ":
                            func_name = request[6:]
                            for f in FUNCTION_LIST:
                                name, param = f.split(":")
                                if name == func_name:
                                    self.sock_send("FUNYS "+f)
                                    break
                            else:
                                self.sock_send("FUNNO "+func_name)
                        elif request[0:5] == "EXERQ":
                            pass
                        elif request[0:5] == "PATCH":
                            pass
                        else:
                            self.sock_send("CMDERR")
                            pass
                        break
                else:  # not in cpl and not regme
                    self.sock_send("REGER")
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
        self.timer = threading.Timer(1.0, self.check_request())
        self.timer.start()
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
                s = self.conn_sock((conn[0], conn[1]))
                s.sendall("GETNL")
                rec = s.recv(100)
                rec.strip()
                if rec == "REGER":
                    success = self.conn_peer((conn[0], conn[1]))
                    if not success:
                        print "Couldn't connect to peer, ", conn
                        CONNECT_POINT_LIST.remove(conn)
                elif rec == "NLIST BEGIN":
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

    def conn_peer(self, addr, i=0):
        s = socket()
        s.connect(addr)
        s.sendall("REGME " + str(SERVER_HOST) + ":" + str(SERVER_PORT))
        ans = s.recv(100)
        i += 1
        if ans.strip() == "REGWA":
            time.sleep(3 * i)
            i += 1
            if i == 3:
                return False
            self.conn_peer(s, i)
        elif ans.strip() == "REGOK":
            return True
        else:
            return False

    def conn_system(self):
        return self.conn_peer(self.conn_sock((gethostname(), 12345)))

    def run(self):
        try:
            if self.conn_system():
                print "Connected to first negotiator." \
                      "Now will try to update NLIST"
                self.update()
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

        app = ip.ImGui(worker_queue, processed_queue, process_lock)
        app.run()
        for t in threads:
            t.join()
    except Exception, ex:
        print __name__, ex
        return


if __name__ == '__main__':
    main()
