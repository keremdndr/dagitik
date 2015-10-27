#!/usr/bin/env python
class myThread (threading.Thread):
	def __init__(self, threadID, clientSocket, clientAddr):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.clientSocket = clientSocket
		self.clientAddr = clientAddr
	def run(self):
		print "Starting Thread-" + str(self.threadID)
		...
		...
		...
		print "Ending Thread-" + str(self.threadID)
		...
		...
		...
s = socket.socket()
host = "0.0.0.0"
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
