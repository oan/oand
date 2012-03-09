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
from oan.dispatcher.message import OANMessageHandshake
from oan.network.serializer import encode, decode
from oan.heartbeat import OANHeartbeat
from oan.network.network_node import OANNetworkNodeState


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
        print "is connected total connection: [%s]" % len(asyncore.socket_map)
        self.send_handshake()

    def handle_accept(self):
        log.info("OANBridge:handle_accept")
        print "is accepted total connection: [%s]" % len(asyncore.socket_map)
        self.send_handshake()

    def send_handshake(self):
        self.out_buffer = self.send_message(OANMessageHandshake.create())

    def got_handshake(self, message):
        # Update with external ip. Sending node is only aware of internal ip,
        # firewall might MASQ/NAT to extetnal ip.
        message.host = self.remote_addr[0]


        self.node = dispatcher().get(message)
        self.node.update(state = OANNetworkNodeState.CONNECTED)

        self.out_queue = self.node.out_queue

    def send_message(self, message):
        raw_message = encode(message)
        if self.node is not None:
            log.info("send_message: %s to %s" % (message.__class__.__name__, self.node.oan_id))
            self.node.add_message_statistic(message.__class__.__name__, out_time = True)

        return raw_message + '\n'

    def read_message(self, raw_message):
        message = decode(raw_message.strip())

        if self.node is not None:
            log.info("read_message: %s from %s" % (message.__class__.__name__, self.node.oan_id))
            self.node.add_message_statistic(message.__class__.__name__, in_time = True)
            self.node.touch()

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
                else:
                    dispatcher().execute(message)

                pos = self.in_buffer.find('\n')

    def writable(self):
        print "OANBridge:writable"

        is_writable = ((len(self.out_buffer) > 0) or (self.out_queue is not None and not self.out_queue.empty()))

        if self.node is not None:
            if self.node.has_heartbeat_state(OANHeartbeat.IDLE):
                print "is idle"
                self.shutdown()
                return True

        return is_writable

    def readable(self):
        return True

    def handle_write(self):
        if (len(self.out_buffer) == 0):
            if self.out_queue is not None and not self.out_queue.empty():
                message = self.out_queue.get()

                if (message == None):
                    print "OANBridge:handle_write closing"
                    self.handle_close()
                    return
                else:
                    self.out_buffer = self.send_message(message)

        sent = self.send(self.out_buffer)
        if self.node is not None:
            print "OUT[%s][%s]" % (self.node.oan_id, self.out_buffer[:sent])

        self.out_buffer = self.out_buffer[sent:]

    def handle_close(self):
        log.info("OANBridge:handle_close")
        asyncore.dispatcher.close(self)
        if self.node is not None:
            self.node.update(state = OANNetworkNodeState.DISCONNECTED)

    def handle_error(self):
        print("OANBridge:handle_error")
        #asyncore.dispatcher.handle_error(self)

        exc_type, exc_value, exc_traceback = sys.exc_info()
        print ("OANBridge:handle_error: %s, %s" % (self.remote_addr, exc_value))

        self.handle_close()

    def shutdown(self):
        log.info("OANBridge:shutdown")
        self.out_queue.put(None)
