#!/usr/bin/env python

import sys
import threading
import Queue
import time

class reader_thread(threading.Thread):
	def __init__(self,threadID,name,file_object,write_queue,read_size):
		threading.Thread.__init__(self)
		self.threadID=threadID
		self.name=name
		self.fo=file_object
		self.wq=write_queue
		self.rs=read_size
	def run(self):
		index=1
		while True:
			text=self.fo.read(self.rs)
			if(text==''):
				break
			text_tup=(text.lower(),index)
			self.wq.put(text_tup)
			index+=1
		global write_finished
		write_finished=True

class writer_thread(threading.Thread):
	def __init__(self,threadID,name,crypt_list,file_object):
		threading.Thread.__init__(self)
		self.ID=threadID
		self.name=name
		self.cl=crypt_list
		self.fo=file_object
	def run(self):
		index=1
		while True:
			queue_lock_crypt.acquire()
			if len(self.cl) !=0:
				for l in self.cl:
					if l[1]==index:
						data=self.cl.pop(self.cl.index(l))
						queue_lock_crypt.release()
						self.fo.write(data[0])
						index+=1
						break
			else:
				queue_lock_crypt.release()
				if write_finished==True:
					break

class crypter_thread(threading.Thread):
	def __init__(self,threadID,name,alphabet,key,write_queue,crypt_list):
		threading.Thread.__init__(self)
		self.threadID=threadID
		self.name=name
		self.alphabet=alphabet
		self.key=key
		self.cl=crypt_list
		self.wq=write_queue
	def run(self):
		while True:
			queue_lock_read.acquire()
			if not self.wq.empty():
				text=self.wq.get()
				queue_lock_read.release()
				data=''
				for c in text[0]:
					if c in self.alphabet:
						data+=self.key[self.alphabet.find(c)]
					else:
						data+=c
				crypt=(data,text[1])
				queue_lock_crypt.acquire()
				self.cl.append(crypt)
				queue_lock_crypt.release()
			else:
				queue_lock_read.release()
				if write_finished:
					break
				
				

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
	write_queue=Queue.Queue(10)
	crypt_list=[]
	
	write_finished=False
	exit_writing=False
	f_read=open("metin.txt","rb")
	write_file="crypted_"+str(s)+"_"+str(n)+"_"+str(l)+".txt"
	f_write=open(write_file,"wb")
	
	threads=[]
	thread=reader_thread(1,"Reader Thread",f_read,write_queue,l)
	thread.start()
	print thread.name + " basladi"
	threads.append(thread)
	for i in range(1,n+1):
		thread=crypter_thread(i+1,"Crypter Thread"+str(i),alphabet,key,write_queue,crypt_list)
		thread.start()
		print thread.name + " basladi"
		threads.append(thread)
	thread=writer_thread(i+2,"Writer Thread",crypt_list,f_write)
	thread.start()
	print thread.name + " basladi"
	threads.append(thread)
	
	for t in threads:
		t.join()
	print "Exiting Main"
