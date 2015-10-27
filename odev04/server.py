#!/usr/bin/env python
import threading
import socket
from time import asctime,sleep
from random import randint
class myThread (threading.Thread):
	def __init__(self, threadID, clientSocket, clientAddr):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.clientSocket = clientSocket
		self.clientAddr = clientAddr
	def run(self):
		print "Starting Thread-" + str(self.threadID)
		try:
			while True:
				asd=self.clientSocket.recv(1024)
				print asd
				#self.clientSocket.sendall("Merhaba, saat suan" + asctime())
		except Exception,Argument:
			print "hata thread:",self.threadID,":",Argument 
		print "Ending Thread-" + str(self.threadID)
threadCounter=0
port = 12345
threads=[]
try:
	s = socket.socket()
	host = socket.gethostname()
	s.bind((host, port))
	s.listen(5)
	while True:
		print "Waiting for connection"
		c, addr = s.accept()
		print 'Got a connection from ', addr
		threadCounter += 1
		thread = myThread(threadCounter, c, addr)
		thread.start()
		threads.append(thread)
except Exception,Argument:
	print Argument
finally:
	s.close()
	for t in threads:
		t.join()
	print "exiting"
	
