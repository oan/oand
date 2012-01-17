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
import uuid
from datetime import datetime, timedelta
from Queue import Queue
from threading import Thread

from oan import dispatcher, node_manager
from oan.event import OANEvent
from oan.node_manager import OANNetworkNode, OANNodeManager
from oan.message import OANMessageHandshake, OANMessageClose
from oan.serializer import encode, decode

class OANBridge(asyncore.dispatcher):

    server = None
    node = None # node that the bridge leading to... is None until handshake is done.
    remote_addr = None
    statistic = None # statistic for my node.

    out_queue = None
    out_buffer = ''

    in_buffer = ''

    def __init__(self, server, sock = None):
        asyncore.dispatcher.__init__(self, sock)
        self.server = server

    def connect(self, addr):
        self.remote_addr = addr
        asyncore.dispatcher.connect(self, addr)

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
        dispatcher().execute(message)

        if not self.writable():
            self.handle_close()

    def got_handshake(self, message):
        #print "OANBridge:got_handshake: %s,%s,%s" % (message.uuid, message.host, message.port)

        remote_host, remote_port = self.remote_addr
        self.node = node_manager().create_node(uuid.UUID(message.uuid), remote_host, message.port, message.blocked)

        self.out_queue = self.node.out_queue
        self.statistic = node_manager().get_statistic()
        dispatcher().execute(message)
        self.server.add_bridge(self)

    def send_message(self, message):
        raw_message = encode(message)
        if self.node is not None:
            print "send_message: %s to %s" % (message.__class__.__name__, self.node.uuid)
            self.node.heartbeat.touch()

        return raw_message + '\n'

    def read_message(self, raw_message):
        message = decode(raw_message.strip())

        if self.node is not None:
            self.node.heartbeat.touch()
            print "read_message: %s from %s" % (message.__class__.__name__, self.node.uuid)

        return message

    def handle_read(self):
        data = self.recv(1024)
        if self.node is not None:
            self.statistic.add_in_transfered(len(data))
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
                    dispatcher().process(message)

                pos = self.in_buffer.find('\n')

    def writable(self):
        #print "OANBridge:writable"
        if self.node is not None:
            if self.node.heartbeat.is_idle():
                self.send_close() # should be moved to oan.loop
                self.server.idle_bridge(self)

        return ((len(self.out_buffer) > 0) or (self.out_queue is not None and not self.out_queue.empty()))

    def readable(self):
        #print "OANBridge:readable"
        return True

    def handle_write(self):
        if (len(self.out_buffer) == 0):
            if self.out_queue is not None and not self.out_queue.empty():
                message = self.out_queue.get()
                self.statistic.out_queue_dec()

                if (message == None):
                    #print "OANBridge:handle_write closing"
                    self.handle_close()
                    return
                else:
                    self.out_buffer = self.send_message(message)

        sent = self.send(self.out_buffer)
        if self.node is not None:
            self.statistic.add_out_transfered(sent)
            #print "OUT[%s][%s]" % (self.node.uuid, self.out_buffer[:sent])

        self.out_buffer = self.out_buffer[sent:]

    def handle_close(self):
        print "OANBridge:handle_close"
        if self.node is not None:
            self.server.remove_bridge(self)

        asyncore.dispatcher.close(self)

    def handle_error(self):
        print "OANBridge:handle_error"
        #asyncore.dispatcher.handle_error(self)

        exc_type, exc_value, exc_traceback = sys.exc_info()
        print "OANBridge:handle_error: %s, %s" % (self.remote_addr, exc_value)

    def shutdown(self):
        print "OANBridge:shutdown"
        self.out_queue.put(None)


