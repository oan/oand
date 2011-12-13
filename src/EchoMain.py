#!/usr/bin/env python


import thread
import asyncore

from EchoServer import EchoServer
from EchoClient import EchoClient

server = EchoServer('localhost', 8080)
server.start()
server.stop()


# client1 = EchoClient('localhost', 8080)

# thread.start_new_thread(asyncore.loop, (2,))
# i = 0


# while i < 1:
#     if len(server.bridges) > 0:
#         i = i + 1
#         server.bridges[0].out_queue.put("my test:" + str(i))

# while 1:
#     while not client1.in_queue.empty():
#         print "Client:" + client1.in_queue.get()


