#!/usr/bin/env python

import sys
import threading
import Queue

class reader_thread(threading.Thread):
	def __init__(self,threadID,name,file_object,read_queue,write_queue,read_size):
		threading.Thread.__init(self)
		self.threadID=threadID
		self.name=name
		self.fo=file_object
		self.rq=read_queue
		self.wq=write_queue
		self.rs=read_size
	def run(self):
		read_from_file(self.fo,self.rs,self.wq)

class writer_thread(threading.Thread):
	def __init__(self,threadID,name,write_queue,file_object,read_size):
		threading.Thread.__init__(self)
		self.ID=threadID
		self.name=name
		self.wq=write_queue
		self.fo=file_object
		self.rs=read_size
	def run(self):
		
class crypter_thread(threading.Thread):
	def __init__(self,threadID,name,alphabet,key,plain_text,crypted_text):
		threading.Thread.__init__(self)
		self.threadID=threadID
		self.name=name
		self.alphabet=alphabet
		self.key=key
		self.plain_text=plain_text
		self.crypted_text=crypted_text
	def run(self):
		print "islem yapiliyor"
		

def crypt_string(alphabet,key,plain):
		
def read_from_file(file_object,read_size,write_queue):
	index=1
	queue_lock_write.acquire()
	while(True)
		text=fo.read(read_size)
		if(text==''):
			break
		text=(text.lower,index)
		write_queue.put(text)
		index+=1
	queue_lock_write.release()
	write_finish=True
	
if len(sys.argv) != 4:
	print "Usage: python odev03_thread.py <shifting> <threads> <block_length>"
	sys.exit("Invalid arguments")
else:
	s=int(sys.argv[1])
	n=int(sys.argv[2])
	l=int(sys.argv[3])
	alphabet="abcdefghijklmnopqrstuvwxyz"
	alphabet_len=len(alphabet)
	head,tail=alphabet[:alphabet_len-s],alphabet[alphabet_len-s:]
	key=tail+head
	key=key.upper()
	
	queue_lock_write=threading.Lock()
	queue_lock_crypt=threading.Lock()
	read_queue=Queue.Queue(10)
	write_queue=Queue.Queue(10)
	
	fo=open("metin.txt","r")
	fo.close()
	


