#!/usr/bin/env python

import sys
import threading

class crypt_thread(threading.Thread):
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

def read_from_file(file_object,read_size):
	return fo.read(read_size)

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
	
	fo=open("metin.txt","r")
	
	


