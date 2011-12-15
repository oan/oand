#!/usr/bin/env python
'''
RPC client.

'''

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import asyncore
import socket
from Queue import Queue

from oan_bridge import OANBridge
from oan_server import OANLoop

class OANClient(OANBridge):

    def __init__(self, host, port):
        OANBridge.__init__(self, None, Queue(), Queue())
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect( (host, port) )

def main():
    client = OANClient('localhost', 8080)
    loop = OANLoop()
    #loop.on_shutdown += client.shutdown()
    loop.start()

    client.out_queue.put("from client 1");
    client.out_queue.put("from client 2");
    client.out_queue.put("from client 3");
    client.out_queue.put("from client 4");
    client.out_queue.put("from client 5");
    client.out_queue.put("from client 6");

if __name__ == "__main__":
    main()
