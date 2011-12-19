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

from datetime import datetime, timedelta
from oan_event import OANEvent
from Queue import Queue
from threading import Thread
from oan_simple_node_manager import OANNode, OANNodeManager

class OANBridge(asyncore.dispatcher):

    server = None
    node_connected = False
    node = None # node that the bridge leading to...
    last_used = None

    out_queue = None
    out_buffer = ''

    in_queue = None
    in_buffer = ''

    def __init__(self, server, node, sock = None):
        asyncore.dispatcher.__init__(self, sock)
        self.out_queue = Queue()
        self.in_queue = Queue()
        self.server = server
        self.node = node

    def handle_connect(self):
        print "OANBridge:handle_connect"
        self.send_handshake()

    def send_handshake(self):
        hs = "%s,%s,%s" % (self.server.node.node_id, self.server.node.host, self.server.node.port)
        self.out_queue.put(hs)

    def read_handshake(self, hs):
        (remote_id, remote_host, remote_port) = hs.split(',')
        print "read_handshake: %s,%s,%s" % (remote_id, remote_host, remote_port)
        self.node = OANNode(remote_id, remote_host, remote_port)
        self.server.add_bridge(self)

    def handle_read(self):
        data = self.recv(1024)
        print "OANBridge:handle_read(%s)" % (data)

        if data:
            self.last_used = datetime.now()
            self.in_buffer += data
            pos = self.in_buffer.find('\n')
            if pos > -1:
                cmd = self.in_buffer[:pos].strip()
                if (not self.node_connected):
                    self.node_connected = True
                    self.read_handshake(cmd)
                else:
                    self.in_queue.put(cmd)

                self.in_buffer = self.in_buffer[pos+1:]

    def writable(self):
        #print "OANBridge:writable"
        if (self.last_used != None):
            diff = datetime.now() - self.last_used
            if (diff > timedelta(seconds=3)):
                self.server.idle_bridge(self)

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
                self.last_used = datetime.now()
                self.out_buffer = data + '\n'

        sent = self.send(self.out_buffer)
        self.out_buffer = self.out_buffer[sent:]

    def handle_close(self):
        print "OANBridge:handle_close"
        self.server.remove_bridge(self)
        asyncore.dispatcher.handle_close(self)

    def handle_error(self):
        print "OANBridge:handle_error"
        #asyncore.dispatcher.handle_error(self)
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print exc_value

    def shutdown(self):
        self.out_queue.put(None)
