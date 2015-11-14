#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 21:15:02 2015

@author: volaka
"""
import sys
import socket
import threading
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import Queue
import time
class ReadThread (threading.Thread):
    def __init__(self, name, csoc, threadQueue, app):
        threading.Thread.__init__(self)
        self.name = name
        self.csoc = csoc
        self.nickname = ""
        self.threadQueue = threadQueue
        self.app = app
        self.message=""
    def incoming_parser(self, data):
        if len(data) == 0:
            return 1
        if len(data) > 3 and not data[3] == " ":
            response = "ERR"
            self.csoc.send(response)
            return 1
        else:
            rest = data[4:]
            if data[0:3] == "BYE":
                msg = "-Server- Sunucuyla baglanti kesildi."
                self.app.cprint(msg)
                return -1
            elif data[0:3] == "ERL":
                msg = "-Server- Nick not registered."
                self.app.cprint(msg)
            elif data[0:3] == "HEL":
                self.nickname = rest
                msg = "-Server- Registered as "+rest
                self.app.cprint(msg)
            elif data[0:3] == "REJ":
                msg = "-Server- Nick has rejected."
                self.app.cprint(msg)
            elif data[0:3] == "MNO":
                msg = "-Server- Private message couldn't send"
                self.app.cprint(msg)
            elif data[0:3] == "MSG":
                msg = rest
                self.app.cprint(msg)
            elif data[0:3] == "SAY":
                msg = rest
                self.app.cprint(msg)
            elif data[0:3] == "SYS":
                msg = rest
                self.app.cprint(msg)
            elif data[0:3] == "LSA":
                splitted = rest.split(":")
                msg = "-Server- Registered nicks: "
                for i in splitted:
                    msg += i + ","
                msg = msg[:-1]
                self.app.cprint(msg)
            elif data[0:3] == "ERR":
                msg = "-Server- Hatali bir giris yaptiniz!"
                self.app.cprint(msg)
            else:
                self.app.cprint("Bilinmeyen protocol")
            return msg
    def run(self):
        while True:
            data = self.csoc.recv(1024)
            print "Reader Thread:Data geldi>",data,type(data)
            self.message = self.incoming_parser(data)
            if self.message==-1:
                break
class WriteThread (threading.Thread):
    def __init__(self, name, csoc, threadQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.csoc = csoc
        self.threadQueue = threadQueue
    def run(self):
        while True:
            if self.threadQueue.qsize() > 0:
                queue_message = self.threadQueue.get()
                try:
                    print "WriterThread:Data yollandi",queue_message
                    self.csoc.send(queue_message)
                except socket.error,e:
                    self.csoc.close()
                    print e
                    break
class ClientDialog(QDialog):
    ''' An example application for PyQt. Instantiate
    and call the run method to run. '''
    def __init__(self, threadQueue):
        self.text=""
        self.threadQueue = threadQueue
        # create a Qt application --- every PyQt app needs one
        self.qt_app = QApplication(sys.argv)
        # Call the parent constructor on the current object
        QDialog.__init__(self, None)
        # Set up the window
        self.setWindowTitle('IRC Client')
        self.setMinimumSize(500, 200)
        # Add a vertical layout
        self.vbox = QVBoxLayout()
        # The sender textbox
        self.sender = QLineEdit("", self)
        # The channel region
        self.channel = QTextBrowser()
        # The send button
        self.send_button = QPushButton('&Send')
        # Connect the Go button to its callback
        self.send_button.clicked.connect(self.outgoing_parser)
        # Add the controls to the vertical layout
        self.vbox.addWidget(self.channel)
        self.vbox.addWidget(self.sender)
        self.vbox.addWidget(self.send_button)
        # A very stretchy spacer to force the button to the bottom
        # self.vbox.addStretch(100)
        # Use the vertical layout for the current window
        self.setLayout(self.vbox)
    def cprint(self, data):
        self.channel.append(data)
    def outgoing_parser(self):
        data = str(self.sender.text())
        if len(data) == 0:
            print "QClient:Data boyutu 0"
            return 1
        if data[0] == "/":
            if data[1:5] == "list":
                self.threadQueue.put("LSQ")
            elif data[1:5] == "quit":
                self.threadQueue.put("QUI")
            elif data[1:4] == "msg":
                try:
                    usr,msg=data[5:].split()
                    self.threadQueue.put("MSG "+usr+":"+msg)
                except Exception,e:
                    self.cprint(e)
                    return 1
            elif data[1:5]=="nick":
                print "QClient:Data yollandi",data
                
                self.threadQueue.put("USR " + data[6:])
            else:
                self.cprint("Local: Command Error.")
        else:
            self.threadQueue.put("SAY " + data)
        self.sender.clear()
    def run(self):
        ''' Run the app and show the main form. '''
        self.show()
        self.qt_app.exec_()
# connect to the server
s = socket.socket()
host = sys.argv[1]
port = int(sys.argv[2])
s.connect((host,port))
sendQueue = Queue.Queue(20)
app = ClientDialog(sendQueue)
# start threads
rt = ReadThread("ReadThread", s, sendQueue, app)
rt.start()
wt = WriteThread("WriteThread", s, sendQueue)
wt.start()
app.run()
rt.join()
wt.join()
s.close()







