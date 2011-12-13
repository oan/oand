#!/usr/bin/env python


import thread
import asyncore
import time

from EchoServer import EchoServer, EchoLoop
from EchoClient import EchoClient

server = EchoServer('localhost', 8080)
client1 = EchoClient('localhost', 8080)


loop = EchoLoop()
loop.start()

time.sleep(2)

if len(server.bridges) > 0:
    print "send"
    server.bridges[0].out_queue.put("my test:")

print "result:" + client1.in_queue.get(True)
loop.stop()
#server.stop()


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


