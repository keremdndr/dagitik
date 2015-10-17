#!/usr/bin/env python

import sys

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
	

