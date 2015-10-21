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
			data_i=(data,index)
			read_queue.put(data_i)
			index+=1
		file_r.close()
	except Ex:
		file_r.close()
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
		crypt_queue.put(('',-1))


def writer(crypt_queue,filename):
	index=1
	f_write=open(filename,"wb")
	crypt_list=[]
	found=False
	while not finish:
		if len(crypt_list)!=0:
			for c in crypt_list:
				if c[1]==index:
					found=True
					f_write.write(c[0])
					crypt_list.pop(crypt_list.index(c)j)
					index+=1
					break
			if found:
				found=False
			else:
				crypt=crypt_queue.get()
				if crypt[1]==index:
					f_write.write(crypt[0])
					index+=1
				else:
					crypt_list.append(crypt)
		else:
			crypt=crypt_queue.get()
			if crypt[1]==index:
				f_write.write(crypt)
				index+=1
			else:
				crypt_list.append(crypt)
		
		
		
		if len(crypt_list)==4:
			for c in crypt_list:
				if c[1]!=-1:
					finish=False
					break
				finish=True
					
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
		
		read_queue=Queue()
		crypt_queue=Queue()
		read_lock=Lock()
		crypt_lock=Lock()
		
		write_file_name="crypted_"+str(s)+"_"+ str(n)+"_"+str(l)+".txt"		
		reader_p=Process(name='Reader Process',target=reader,args=(l,read_queue,))
		reader_p.start()
				
		processes=[]
		for i in range(0,n):
			p=Process(name='Crypter Process '+str(i+1),target=crypter,args=(alphabet,key,read_queue,crypt_queue,))
			p.start()
			processes.append(p)
		
		writer_p=Process(name='Writer Process',target=writer,args=(crypt_queue,write_file_name,)
if __name__ == '__main__':
	main()	
