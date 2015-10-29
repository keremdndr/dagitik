#!/usr/bin/env python
import threading
import socket
from time import asctime,sleep
from random import randint
class serverSend (threading.Thread):
	def __init__(self,threadID,clientSocket,clientAddr):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.clientSocket = clientSocket
		self.clientAddr= clientAddr
	def run(self):
		try:
			while not Stop:
				sleep(randint(1,60))
				self.clientSocket.sendall("Merhaba, saat suan " + asctime())
		except Exception, e:
			print "Hata thread",threadID,":",e
class serverReceive (threading.Thread):
	def __init__(self, threadID, clientSocket, clientAddr):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.clientSocket = clientSocket
		self.clientAddr = clientAddr
	def run(self):
		print "Starting Thread-" + str(self.threadID)
		try:
			global Stop
			while not Stop:
				rec=self.clientSocket.recv(1024)
				if rec != "":
					print rec
				elif rec == "exit":
					Stop = True
		except Exception,e:
			print "Hata thread",self.threadID,":",e 
		print "Ending Thread-" + str(self.threadID)
threadCounter=0
port = 12345
threads=[]
Stop=False
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
		thread = serverReceive(threadCounter, c, addr)
		thread.start()
		threads.append(thread)
		threadCounter +=1
		thread = serverSend(threadCounter,c,addr)
		thread.start()
		threads.append(thread)
except Exception,Argument:
	print Argument
finally:
	Stop=True
	s.close()
	for t in threads:
		t.join()
	print "exiting"
	
