#!/usr/bin/env python

import sys

alphabet="abcdefghijklmnopqrstuvwxyz"
alphabet_len=len(alphabet)


if len(sys.argv) != 4:
	print "Usage: python odev03_thread.py <shifting> <threads> <block_length>"
	sys.exit("Invalid arguments")
else:
	s=sys.argv[1]
	n=sys.argv[2]
	l=sys.argv[3]

