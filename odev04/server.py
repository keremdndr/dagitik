#!/usr/bin/env python
import threading
import socket
from time import asctime
from random import randint
class myThread (threading.Thread):
	def __init__(self, threadID, clientSocket, clientAddr):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.clientSocket = clientSocket
		self.clientAddr = clientAddr
	def run(self):
		print "Starting Thread-" + str(self.threadID)
		while True:
			rand = randint(1,100)
			wait(rand) 
			self.clientSocket.sendall("Merhaba, saat şuan" + time.asctime())
		print "Ending Thread-" + str(self.threadID)
s = socket.socket()
host = socket.gethostname()
port = 12345
s.bind((host, port))
s.listen(5)
while True:
	print "Waiting for connection"
	c, addr = s.accept()
	print 'Got a connection from ', addr
	threadCounter += 1
	thread = myThread(threadCounter, c, addr)
	thread.start()
