#!/usr/bin/env python

import sys
import time
from multiprocessing import Process,Queue,Lock

def reader(fo,rs,wq):
	index=1
	while True:
		text=fo.read(rs)
		if(text==''):
			break
		text_tup=(text.lower(),index)
		wq.put(text_tup)
		index+=1

def writer(fo,cl):
	index=1
	found=False
	while True:
		queue_lock_crypt.acquire()
		if len(cl) !=0:
			for l in cl:
				if l[1]==index:
					data=cl.pop(cl.index(l))
					queue_lock_crypt.release()
					fo.write(data[0])
					index+=1
					found=True
					break
			if not found:
				queue_lock_crypt.release()
			else:
				found=False
		else:
			queue_lock_crypt.release()
			if crypt_finished:
				break

def crypter(alphabet,key,wq,cl):
	while True:
		queue_lock_read.acquire()
		if not wq.empty():
			text=wq.get()
			queue_lock_read.release()
			data=''
			for c in text[0]:
				if c in alphabet:
					data+=key[alphabet.find(c)]
				else:
					data+=c
			crypt=(data,text[1])
			queue_lock_crypt.acquire()
			cl.append(crypt)
			queue_lock_crypt.release()
		else:
			queue_lock_read.release()
			if read_finished:
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
	
	queue_lock_read=Lock()
	queue_lock_crypt=Lock()
	write_queue=Queue(20)
	crypt_list=[]
	
	read_finished=False
	crypt_finished=False
	f_read=open("metin.txt","rb")
	write_file="crypted_"+str(s)+"_"+str(n)+"_"+str(l)+".txt"
	f_write=open(write_file,"wb")
	
	processes=[]
	process_r=Process(target=reader,args=(f_read,l,write_queue))
	process_r.start()
	for i in range(1,n+1):
		process_c=Process(target=crypter,args=(alphabet,key,write_queue,crypt_list))
		process_c.start()
		processes.append(process_c)
	process_w=Process(target=writer,args=(f_write,crypt_list))
	process_w.start()
	
	process_r.join()
	read_finished=True
	print "Read Thread Finished"
	for t in processes:
		t.join()
	print "Crypting finished"
	crypt_finished=True
	process_w.join()
	f_read.close()
	f_write.close()
	print "Write Thread Finished"
	print "Exiting Main"
