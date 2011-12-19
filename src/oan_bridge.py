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

from oan import node_manager
from datetime import datetime, timedelta
from oan_event import OANEvent
from Queue import Queue
from threading import Thread
from oan_simple_node_manager import OANNode, OANNodeManager
from oan_message import OANMessageHandshake
import oan_serializer

class OANBridge(asyncore.dispatcher):

    server = None
    node = None # node that the bridge leading to... is None to handshake is done.
    last_used = None

    out_queue = None
    out_buffer = ''

    in_queue = None
    in_buffer = ''

    def __init__(self, server, sock = None):
        asyncore.dispatcher.__init__(self, sock)
        self.server = server

    def handle_connect(self):
        print "OANBridge:handle_connect"
        self.send_handshake()

    def send_handshake(self):
        my_node = node_manager().get_my_node()
        print "send_handshake: %s,%s,%s" % (my_node.uuid, my_node.host, my_node.port)
        self.send_message(
            OANMessageHandshake.create(my_node.uuid, my_node.host, my_node.port)
        )

    def read_handshake(self, raw_message):
        message = self.read_message(raw_message)
        print "read_handshake: %s,%s,%s" % (message.uuid, message.host, message.port)
        message.execute()

        if (node_manager().exist_node(message.uuid)):
            self.node = node_manager().get_node(message.uuid)
        else:
            self.node = node_manager().create_node(message.uuid, message.host, message.port)

        self.out_queue = self.node.out_queue
        self.in_queue = self.node.in_queue
        self.server.add_bridge(self)

    def send_message(self, message):
        raw_message = oan_serializer.encode(message)
        print "send_message: %s" % (message.__class__.__name__)
        self.touch_last_used()
        self.out_buffer = raw_message + '\n'

    def read_message(self, raw_message):
        message = oan_serializer.decode(raw_message)
        print "read_message: %s" % (message.__class__.__name__)
        return message

    def handle_read(self):
        data = self.recv(1024)
        print "OANBridge:handle_read(%s)" % (data)

        if data:
            self.touch_last_used()
            self.in_buffer += data
            pos = self.in_buffer.find('\n')
            if pos > -1:
                cmd = self.in_buffer[:pos].strip()
                if (self.node is None):
                    self.read_handshake(cmd)
                else:
                    self.in_queue.put(self.read_message(cmd))

                self.in_buffer = self.in_buffer[pos+1:]

    def writable(self):
        #print "OANBridge:writable"
        if (self.last_used != None):
            diff = datetime.now() - self.last_used
            if (diff > timedelta(seconds=3)):
                self.server.idle_bridge(self)

        return ((len(self.out_buffer) > 0) or (self.out_queue is not None and not self.out_queue.empty()))

    def handle_write(self):
        if (len(self.out_buffer) == 0):
            if self.out_queue is not None and not self.out_queue.empty():
                message = self.out_queue.get_nowait()

                if (message == None):
                    print "OANBridge:handle_write closing"
                    self.close()
                    return
                else:
                    self.send_message(message)


        sent = self.send(self.out_buffer)
        self.out_buffer = self.out_buffer[sent:]

    def handle_close(self):
        print "OANBridge:handle_close"
        if (self.node is not None):
            self.server.remove_bridge(self)

        asyncore.dispatcher.handle_close(self)

    def handle_error(self):
        asyncore.dispatcher.handle_error(self)
        exc_type, exc_value, exc_traceback = sys.exc_info()
        #print "OANBridge:handle_error: %s" % exc_value

    def shutdown(self):
        print "OANBridge:shutdown"
        self.out_queue.put(None)

    def touch_last_used(self):
        self.last_used = datetime.now()
