#!/usr/bin/env python

import sys
import time
from multiprocessing import Process,Queue,Lock,current_process()

def reader(read_size,read_queue):
	try:
		p=current_process()
		file_r=open("metin.txt","rb")
		data='x'
		index=1
		while data!='':
			print p.name
			data=file_r.read(read_size)
			data_i=(data,i)
			read_queue.put(data_i)
			i+=1
	except Ex:
		print "in "+p.name+" error "+ Ex.strerror 
	
def crypter(alphabet,key,read_queue,crypt_queue):
	data=''
	crypt=''
	try:
		read_lock.acquire()
		while not read_queue.empty():
			text=read_queue.get()
			read_lock.release()
			for c in text[0]:
				if c in alphabet:
					data+=key[alphabet.find(c)]
				else:
					data+=c
				
				crypt=(data,text[1])
				crypt_lock.acquire()
				crypt_queue.put(crypt)
				crypt_lock.release()


def writer():

def main():
	if len(sys.argv) != 4:
		print "Usage: python odev03_process.py <shifting> <threads> <block_length>"
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
					
		reader_p=Process(name='Reader Process',target=reader)
		reader_p.start()
				
		processes=[]
		for i in range(0,n):
			p=Process(name='Crypter Process '+str(i+1),target=crypter)
			p.start()
			processes.append(p)
		
		writer_p=Process(name='Writer Process',target=writer)
if __name__ == '__main__':
	main()	
