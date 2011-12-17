#!/usr/bin/env python
'''
RPC bridge to queue and send request between oan client and server.

'''

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import asyncore
import socket
import thread
import sys

from oan_event import OANEvent
from Queue import Queue
from threading import Thread

class OANBridge(asyncore.dispatcher):

    server = None
    connected_to = None

    out_queue = Queue()
    out_buffer = ''

    in_queue = Queue()
    in_buffer = ''

    def __init__(self, server, sock = None):
        asyncore.dispatcher.__init__(self, sock)
        self.server = server

    def handle_connect(self):
        print "OANBridge:handle_connect"
        self.handshake()

    def handshake(self):
        self.out_queue.put(self.server.node_id)

    def handle_read(self):
        data = self.recv(1024)
        print "OANBridge:handle_read(%s)" % (data)

        if data:
            self.in_buffer += data
            pos = self.in_buffer.find('\n')
            if pos > -1:
                cmd = self.in_buffer[:pos].strip()

                if (self.connected_to == None):
                    self.connected_to = cmd
                    self.server.add_bridge(self)
                else:
                    self.in_queue.put(cmd)

                self.in_buffer = self.in_buffer[pos+1:]

    def writable(self):
        #print "OANBridge:writable"
        return not self.out_queue.empty()

    def handle_write(self):
        if (len(self.out_buffer) == 0):
            data = self.out_queue.get(False)
            if (data == None):
                print "OANBridge:handle_write closing"
                self.close()
                return

            print "OANBridge:handle_write (%s)" % (data)
            if data:
                self.out_buffer = data + '\n'

        sent = self.send(self.out_buffer)
        self.out_buffer = self.out_buffer[sent:]

    def handle_close(self):
        print "OANBridge:handle_close"
        self.server.remove_bridge(self)
        asyncore.dispatcher.handle_close(self)

    def handle_error(self):
        print "OANBridge:handle_error"
        asyncore.dispatcher.handle_error(self)
        #exc_type, exc_value, exc_traceback = sys.exc_info()
        #print exc_value

    def shutdown(self):
        self.out_queue.put(None)
