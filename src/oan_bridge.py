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
from oan_node_manager import OANNetworkNode, OANNodeManager
from oan_message import OANMessageHandshake, OANMessageClose
import oan_serializer

class OANBridge(asyncore.dispatcher):

    server = None
    node = None # node that the bridge leading to... is None to handshake is done.

    out_queue = None
    out_buffer = ''

    in_queue = None
    in_buffer = ''

    def __init__(self, server, sock = None):
        asyncore.dispatcher.__init__(self, sock)
        self.server = server

    def handle_connect(self):
        #print "OANBridge:handle_connect"
        self.send_handshake()

    def handle_accept(self):
        #print "OANBridge:handle_accept"
        self.send_handshake()

    def send_handshake(self):
        my_node = node_manager().get_my_node()
        #print "OANBridge:send_handshake: %s,%s,%s" % (my_node.uuid, my_node.host, my_node.port)
        self.out_buffer = self.send_message(
            OANMessageHandshake.create(my_node.uuid, my_node.host, my_node.port, my_node.blocked)
        )

    def send_close(self):
        my_node = node_manager().get_my_node()
        print "OANBridge:send_close: %s,%s,%s" % (my_node.uuid, my_node.host, my_node.port)
        self.out_buffer = self.send_message(
            OANMessageClose.create(my_node.uuid)
        )

    def got_close(self, message):
        print "OANBridge:got_close: %s" % (message.uuid)
        message.execute()

        if not self.writable():
            self.handle_close()

    def got_handshake(self, message):
        #print "OANBridge:got_handshake: %s,%s,%s" % (message.uuid, message.host, message.port)
        message.execute()

        self.node = node_manager().create_node(message.uuid, message.host, message.port)
        self.node.blocked = message.blocked

        self.out_queue = self.node.out_queue
        self.in_queue = node_manager().dispatcher.queue

        self.server.add_bridge(self)

    def send_message(self, message):
        raw_message = oan_serializer.encode(message)
        #print "send_message: %s" % (message.__class__.__name__)
        if self.node is not None:
            self.node.heartbeat.touch()

        return raw_message + '\n'

    def read_message(self, raw_message):
        message = oan_serializer.decode(raw_message.strip())

        if self.node is not None:
            self.node.heartbeat.touch()

        #print "read_message: %s" % (message.__class__.__name__)
        return message

    def handle_read(self):
        data = self.recv(1024)
        #if self.node is not None:
           # print "IN[%s][%s]" % (self.node.uuid, data)

        if data:
            self.in_buffer += data

            pos = self.in_buffer.find('\n')
            while pos > -1:
                cmd = self.in_buffer[:pos]
                self.in_buffer = self.in_buffer[pos+1:]

                #print "CMD[%s]" % cmd
                message = self.read_message(cmd)
                if isinstance(message, OANMessageHandshake):
                    self.got_handshake(message)
                elif isinstance(message, OANMessageClose):
                    self.got_close(message)
                else:
                    self.in_queue.put(message)

                pos = self.in_buffer.find('\n')

    def writable(self):
        #print "OANBridge:writable"
        if self.node is not None:
            if self.node.heartbeat.is_idle():
                self.send_close() # should be moved to oan_loop
                self.server.idle_bridge(self)

        return ((len(self.out_buffer) > 0) or (self.out_queue is not None and not self.out_queue.empty()))

    def readable(self):
        #print "OANBridge:readable"
        return True

    def handle_write(self):
        if (len(self.out_buffer) == 0):
            if self.out_queue is not None and not self.out_queue.empty():
                message = self.out_queue.get()

                if (message == None):
                    #print "OANBridge:handle_write closing"
                    self.handle_close()
                    return
                else:
                    self.out_buffer = self.send_message(message)

        sent = self.send(self.out_buffer)
        #if self.node is not None:
            #print "OUT[%s][%s]" % (self.node.uuid, self.out_buffer[:sent])
        self.out_buffer = self.out_buffer[sent:]

    def handle_close(self):
        print "OANBridge:handle_close"
        if self.node is not None:
            self.server.remove_bridge(self)

        asyncore.dispatcher.close(self)

    def handle_error(self):
        print "OANBridge:handle_error"
        asyncore.dispatcher.handle_error(self)
        exc_type, exc_value, exc_traceback = sys.exc_info()
        #print "OANBridge:handle_error: %s" % exc_value

    def shutdown(self):
        print "OANBridge:shutdown"
        self.out_queue.put(None)

