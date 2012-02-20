#!/usr/bin/env python
'''
RPC bridge to queue and send messages between oan client and server.

'''

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import asyncore
import socket
import sys

from oan.manager import dispatcher
from oan.util import log
from oan.dispatcher.message import OANMessageHandshake, OANMessageClose
from oan.network.serializer import encode, decode


class OANBridge(asyncore.dispatcher):
    server = None

    # Remote node that the bridge is connected to.
    node = None
    remote_addr = None

    out_queue = None
    out_buffer = ''

    in_buffer = ''

    def __init__(self, server, sock = None):
        asyncore.dispatcher.__init__(self, sock)
        self.server = server

    def connect(self, host, port):
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.remote_addr = (host, port)
        asyncore.dispatcher.connect(self, self.remote_addr)

    def handle_connect(self):
        log.info("OANBridge:handle_connect")
        print "is connected"
        self.send_handshake()

    def handle_accept(self):
        log.info("OANBridge:handle_accept")
        self.send_handshake()

    def send_handshake(self):
        self.out_buffer = self.send_message(OANMessageHandshake.create())

    def got_handshake(self, message):
        # Update with external ip. Sending node is only aware of internal ip,
        # firewall might MASQ/NAT to extetnal ip.
        message.host = self.remote_addr[0]

        self.node = dispatcher().get(message)
        self.out_queue = self.node.out_queue
        self.server.add_bridge(self)

    def send_close(self):
        """
        Ask remote to close socket.

        Give the remote host a chance to send all messages in queue.

        """
        (heartbeat_value, oan_id, name, port, host, state, blocked) = dispatcher().get(OANCommandStaticGetNodeInfo)

        log.info("OANBridge:send_close: %s,%s,%s,%s" % (oan_id, host, port, blocked))
        self.out_buffer = self.send_message(
            OANMessageClose.create(oan_id)
        )

    def got_close(self, message):
        log.info("OANBridge:got_close: %s" % (message.oan_id))
        dispatcher().execute(message)

        if not self.writable():
            self.handle_close()

    def send_message(self, message):
        raw_message = encode(message)
        if self.node is not None:
            log.info("send_message: %s to %s" % (message.__class__.__name__, self.node.oan_id))

        return raw_message + '\n'

    def read_message(self, raw_message):
        message = decode(raw_message.strip())

        if self.node is not None:
            self.node.heartbeat.touch()
            log.info("read_message: %s from %s" % (message.__class__.__name__, self.node.oan_id))

        return message

    def handle_read(self):
        data = self.recv(1024)
        if self.node is not None:
            log.info("IN[%s][%s]" % (self.node.oan_id, data))

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
                    dispatcher().execute(message)

                pos = self.in_buffer.find('\n')

    def writable(self):
        #print "OANBridge:writable"
        #if self.node is not None:
        #
        #   move is_idle to node object.
        #
        #    if self.node.heartbeat.is_idle():
        #        self.send_close() # should be moved to oan.loop
        #        self.server.idle_bridge(self)

        return ((len(self.out_buffer) > 0) or (self.out_queue is not None and not self.out_queue.empty()))

    def readable(self):
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
            #print "OUT[%s][%s]" % (self.node.oan_id, self.out_buffer[:sent])

        self.out_buffer = self.out_buffer[sent:]

    def handle_close(self):
        log.info("OANBridge:handle_close")
        if self.node is not None:
            self.server.remove_bridge(self)

        asyncore.dispatcher.close(self)

    def handle_error(self):
        print("OANBridge:handle_error")
        #asyncore.dispatcher.handle_error(self)

        exc_type, exc_value, exc_traceback = sys.exc_info()
        print ("OANBridge:handle_error: %s, %s" % (self.remote_addr, exc_value))

        self.handle_close()

    def shutdown(self):
        log.info("OANBridge:shutdown")
        self.out_queue.put(None)
