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
    def __init__(self, name, csoc, threadQueue, app,lock):
        threading.Thread.__init__(self)
        self.name = name
        self.csoc = csoc
        self.nickname = ""
        self.threadQueue = threadQueue
        self.app = app
        self.message=""
        self.lock = lock
    def incoming_parser(self, data):
        print data
        if len(data) == 0:
            return 1
        if len(data) > 3 and not data[3] == " ":
            response = "ERR"
            self.lock.acquire()
            self.csoc.send(response)
            self.lock.release()
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
                return -1
            elif data[0:3] == "MNO":
                msg = "-Server- Private message couldn't send"
                self.app.cprint(msg)
            elif data[0:3] == "MSG":
                msg = rest
                self.app.cprint(msg)
            elif data[0:3] == "MOK":
                pass
            elif data[0:3] == "SAY":
                msg = rest
                self.app.cprint(msg)
            elif data[0:3] == "SOK":
                msg = "Mesaj gonderimi basarili"
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
                msg="Bilinmeyen protocol"
                self.app.cprint(msg)
            return msg
    def run(self):
        while True:
            data = self.csoc.recv(1024)
            self.message = self.incoming_parser(data)
            if self.message==-1:
                break
        self.threadQueue.put("EOC")
        s.close()
class WriteThread (threading.Thread):
    def __init__(self, name, csoc, threadQueue,lock):
        threading.Thread.__init__(self)
        self.name = name
        self.csoc = csoc
        self.threadQueue = threadQueue
        self.lock = lock
    def run(self):
        while True:
            if self.threadQueue.qsize() > 0:
                queue_message = self.threadQueue.get()
                print queue_message
                if queue_message == "EOC":                   #end of connection
                    break
                try:
                    self.lock.acquire()
                    self.csoc.send(queue_message)
                    self.lock.release()
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
                send_mess = "LSQ"
            elif data[1:5] == "quit":
                send_mess = "QUI"
            elif data[1:4] == "msg":
                usr,msg=data[5:].split()
                send_mess == "MSG "+usr+":"+msg
            elif data[1:5]=="nick":                
                send_mess = "USR " + data[6:]
            else:
                send_mess = "ERR "
                self.cprint("Local: Command Error.")
        else:
            send_mess = "SAY "+data
        print "QClient:Data yollandi",send_mess
        self.threadQueue.put(str(send_mess))
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
app.daemon=True
lock=threading.Lock()
# start threads
rt = ReadThread("ReadThread", s, sendQueue, app,lock)
rt.daemon=True
rt.start()
wt = WriteThread("WriteThread", s, sendQueue,lock)
wt.daemon=True
wt.start()
app.run()
rt.join()
wt.join()
s.close()







