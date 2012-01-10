#!/usr/bin/env python


import thread
import time
from threading import *
import Queue

class EchoProducer(Thread):

    def __init__(self,itemq):
        Thread.__init__(self)
        self.itemq=itemq

    def run(self):

        itemq=self.itemq
        i=0
        while 1 :

            print currentThread(),"Produced One Item:",i
            itemq.put(i,1)
            i+=1
            time.sleep(1)


class EchoConsumer(Thread):

    def __init__(self,itemq):
        Thread.__init__(self)
        self.itemq=itemq

    def run(self):
        itemq=self.itemq

        while 1:
            time.sleep(2)
            it=itemq.get(1)
            print currentThread(),"Consumed One Item:",it


if __name__=="__main__":

    q=Queue.Queue(10)

    pro=Producer(q)
    cons1=Consumer(q)
    cons2=Consumer(q)

    pro.start()
    cons1.start()
    cons2.start()
    while 1: pass
