#!/usr/bin/env python

import sys
import threading
import Queue
import time

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
	def __init__(self,threadID,name,crypt_queue,file_object,read_size):
		threading.Thread.__init__(self)
		self.ID=threadID
		self.name=name
		self.cq=crypt_queue
		self.fo=file_object
		self.rs=read_size
	def run(self):
		write_to_file(self.fo,read_size,self.cq)
class crypter_thread(threading.Thread):
	def __init__(self,threadID,name,alphabet,key,write_queue,crypt_queue):
		threading.Thread.__init__(self)
		self.threadID=threadID
		self.name=name
		self.alphabet=alphabet
		self.key=key
		self.cq=crypt_queue
		self.wq=write_queue
	def run(self):
		crypt_string(self.alphabet,self.key)
		

def crypt_string(alphabet,key,write_queue,crypt_queue):
	while True:
		queue_lock_read.acquire()
		if not write_queue.empty()
			text=write_queue.get()
			queue_lock_read.release()
			data=''
			for c in text[0]:
				if c in alphabet:
					data+=key[alphabet.find(c)]
				else:
					data+=c
			crypt=(data,text[1])
			crypt_queue.put(crypt)
		else:
			queue_lock_read.release()
			if write_finished:
				break
						
def read_from_file(file_object,read_size,write_queue):
	index=1
	while True
		text=fo.read(read_size)
		if(text==''):
			break
		text=(text.lower,index)
		write_queue.put(text)
		index+=1
	global write_finished
	write_finished=True
	
def write_to_file(file_object,crypt_queue):
	index=1
	while True:
		queue_lock_crypt.acquire()
		if not crypt_queue.empty():
			data=crypt_queue.get()	
			queue_lock_crypt.release()
			file_object.write(data[0])
			index+=1
		else:
			queue_lock_crypt.release()
			time.sleep(1)

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
	
	queue_lock_read=threading.Lock()
	queue_lock_crypt=threading.Lock()
	read_queue=Queue.Queue(10)
	write_queue=Queue.Queue(30)
	
	write_finished=False
	
	fo=open("metin.txt","r")
	fo.close()
	


