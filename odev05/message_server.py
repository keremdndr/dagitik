#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 18:05:17 2015

@author: volaka
"""
import threading
import socket
import time
import Queue

class WriteThread (threading.Thread):
    def __init__(self, name, cSocket, address, threadQueue, logQueue ):
        threading.Thread.__init__(self)
        self.name = name
        self.cSocket = cSocket
        self.address = address
        self.lQueue = logQueue
        self.tQueue = threadQueue
   
    def run(self):
        self.lQueue.put("Starting " + self.name)
        while True:
            
            # burasi kuyrukta sirasi gelen mesajlari
            # gondermek icin kullanilacak
            if self.tQueue.qsize() > 0:
                queue_message = self.tQueue.get()
                # gonderilen ozel mesajsa
                if queue_message[2]=="MSG":
                    message_to_send = "MSG " + queue_message[1]+" "+queue_message[3]
                # genel mesajsa
                elif queue_message[2]=="SAY":
                    message_to_send = "SAY "+queue_message[1]+" "+queue_message[3]
                # hicbiri degilse sistem mesajidir
                elif queue_message[2]=="QUI":
                    break
                else:
                    message_to_send = "SYS "+queue_message[3]
                self.cSocket.sendall(message_to_send)
                    
        self.lQueue.put("Exiting " + self.name)
    
class ReadThread (threading.Thread):
    def __init__(self, name, cSocket, address, threadQueue,logQueue,fihrist):
        threading.Thread.__init__(self)
        self.nickname=""
        self.name = name
        self.cSocket = cSocket
        self.address = address
        self.lQueue = logQueue
        self.fihrist = fihrist
        self.tQueue=threadQueue
    def csend(self,data):
        self.cSocket.sendall(data)
    def parser(self, data):
        dataList = data.strip().split()
        if len(dataList)!=0:
            #USR kayitli degilse ve ilk istek USR degilse login hatasi
            if not self.nickname and not dataList[0] == "USR":
                response = "ERL"
                self.csend(response)
            #USR girisi   
            elif dataList[0] == "USR":
                if not self.fihrist.has_key(dataList[1]):
                    self.nickname = dataList[1]
                    response = "HEL " + self.nickname
                    self.fihrist[dataList[1]]=self.tQueue 
                    self.csend(response)
                    self.lQueue.put(self.nickname + " has joined.")
                    queue_message=(None,self.nickname,"SYS",self.nickname+" has joined.")
                    for q in self.fihrist.values():
                        q.put(queue_message)
                    return 0
                else:
                    response = "REJ"
                    self.csend(response)
                    self.cSocket.close()
                    return 1
                    
            elif dataList[0] == "QUI":
                response = "BYE " + self.nickname
                self.fihrist.pop(self.nickname)
                self.lQueue.put(self.nickname+" has left.")
                self.csend(response)
                queue_message=(None,self.nickname,"SYS",self.nickname+" has left.")
                for q in self.fihrist.values():
                    q.put(queue_message)
                self.cSocket.close()
                return "QUI"
                
            elif dataList[0] == "LSQ":
                response = "LSA "
                for k in self.fihrist.keys():
                    response+=k
                    response+=":"
                self.csend(response)
                self.lQueue.put(self.nickname+" has requested for user list.")
                return 0
            
            elif dataList[0] == "TIC":
                response = "TOC"
                self.csend(response)
                return 0
            
            elif dataList[0] == "SAY":
                response= "SOK"
                message_type="SAY"
                queue_message = (None,self.nickname,message_type,dataList[1])
                for q in self.fihrist.values():
                    q.put(queue_message)
                self.csend(response)
                return 0
                
            elif dataList[0] == "MSG":
                to_nickname,message = dataList[1].split(":")
                if not to_nickname in self.fihrist.keys():
                    response = "MNO"
                else:
                    message_type="MSG"
                    queue_message = (to_nickname, self.nickname, message_type,message)
                    # gonderilecek threadQueueyu fihristten alip icine yaz
                    self.fihrist[to_nickname].put(queue_message)
                    response = "MOK"
                self.csend(response)
                return 0
            else:
            # bir seye uymadiysa protokol hatasi verilecek
                response = "ERR"
                self.csend(response)
                return 1
            
    def run(self):
        self.lQueue.put("Starting " + self.name)
        while True:
            
            incoming_data=self.cSocket.recv(1024)
            return_message = self.parser(incoming_data)
            if return_message=="QUI":
                self.tQueue.put((None,None,"QUI",None))
                break
         
        self.lQueue.put("Exiting " + self.name)
        
class LoggerThread (threading.Thread):
    def __init__(self, name, logQueue, logFileName):
        threading.Thread.__init__(self)
        self.name = name
        self.lQueue = logQueue
        # dosyayi appendable olarak ac
        self.fid = open(logFileName,"a+")
    def log(self,message):
        # gelen mesaji zamanla beraber bastir
        t = time.ctime()
        print t+":"+message
        self.fid.write(t + ":" + message+"\n")
        self.fid.flush()
    def run(self):
        self.log("Starting " + self.name)
        while True:
            if not self.lQueue.empty():
                to_be_logged = self.lQueue.get()
                self.log(to_be_logged)
        self.log("Exiting" + self.name)
        self.fid.close()
    
port=12345
threadCounter=0
threads=[]
fihrist=dict()
s=None
host=None
try:
    logQueue= Queue.Queue(30)
    s=socket.socket()
    host=socket.gethostname()
    s.bind((host,port))
    s.listen(5)
    thread=LoggerThread("Logger Thread",logQueue,"log.txt")
    thread.daemon=True
    thread.start()
    threads.append(thread)
    threadCounter+=1
except Exception,e:
    print e
    s.close()
while True:
    try:
        
        print "Wating for connection"
        c,addr = s.accept()
        text = "Got a connection from"+str(addr)
        logQueue.put(text)
        threadQueue=Queue.Queue(10)
        thread=WriteThread("Writer Thread",c,addr,threadQueue,logQueue)
        thread.daemon=True       
        thread.start()
        threads.append(thread)
        threadCounter+=1
        thread=ReadThread("Reader Thread",c,addr,threadQueue,logQueue,fihrist)
        thread.daemon=True 
        thread.start()
        threads.append(thread)
        threadCounter+=1
    except Exception,e:
        logQueue.put(e)
        print e