#!/usr/bin/env python


import thread
import asyncore, socket

from EchoServer import EchoServer
from EchoClient import EchoClient

server = EchoServer('localhost', 8080)
client1 = EchoClient('localhost', 8080)

thread.start_new_thread(asyncore.loop, ())
i = 0
while 1:
    i = i + 1
    import time
    time.sleep(1)
    if len(server.bridges) > 0:
        server.bridges[0].out_queue.put("my test:" + str(i))

    while not client1.in_queue.empty():
        print "Client:" + client1.in_queue.get()

