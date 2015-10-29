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
			while True:
				sleep(randint(1,60))
				self.clientSocket.sendall("Merhaba, saat suan " + asctime())
		except Exception, e:
			print "Hata thread sender",threadID,":",e
class serverReceive (threading.Thread):
	def __init__(self, threadID, clientSocket, clientAddr):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.clientSocket = clientSocket
		self.clientAddr = clientAddr
	def run(self):
		print "Starting Thread-" + str(self.threadID)
		try:
			while True:
				rec=self.clientSocket.recv(1024)
				print rec
				ans="Peki "+str(self.clientAddr[0])+":"+str(self.clientAddr[1])
				if rec != "":					
					self.clientSocket.sendall(ans)
				elif rec == "exit":
					break
					
		except Exception,e:
			print "Hata thread receiver",str(self.threadID),":",e 
		print "Ending Thread-",str(self.threadID)
threadCounter=0
port = 12345
threads=[]
try:
	s=socket.socket()
	host=socket.gethostname()
	s.bind((host,port))
	s.listen(5)
except Exception,e:
	print e
while True:
	try:
		print "Waiting for connection"
		c, addr = s.accept()
		print 'Got a connection from ', addr
		threadCounter += 1
		thread = serverReceive(threadCounter, c, addr)
		thread.start()
		threads.append(thread)
		thread = serverSend(threadCounter,c,addr)
		thread.start()
		threads.append(thread)
	except Exception,Argument:
		print Argument
		s.close()
		break

