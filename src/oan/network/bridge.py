#!/usr/bin/env python
"""
A network bridge used to send messages between two nodes.

@TODO: Handle node elsewhere or unittest the node code.

"""

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import asyncore
import socket
import sys
import traceback

from oan.util import log
from oan.network.serializer import encode, decode
from oan.heartbeat import OANHeartbeat
from oan.network.network_node import OANNetworkNodeState


class OANBridge(asyncore.dispatcher):
    """
    A network bridge used to send messages between two nodes.

    CALLBACKS

    connect_callback(bridge)
        Called when a connection has been established, that was initialized
        from this host.

    received_callback(bridge, message)
        Called when a message has been received from a remote host.

    close_callback(bridge)
        Called when the connection has closed.

    """
    # Callbacks
    connect_callback = None
    received_callback = None
    close_callback = None

    # Messages that should be sent to remote host.
    out_queue = None

    # Remote host that the bridge is connected to.
    node = None

    # Tuple of host and port to remote host.
    _remote_addr = None

    # Buffer of data to send to remote host.
    _out_buffer = ''

    # Buffer of data received from remote host.
    in_buffer = ''

    def __init__(self, sock = None):
        asyncore.dispatcher.__init__(self, sock)
        self.connect_callback = lambda bridge : None
        self.received_callback = lambda bridge, msg : None
        self.close_callback = lambda bridge : None

    def connect(self, host, port):
        """
        Connect to a remote host and establish the bridge.

        """
        log.info("OANBridge:connect %s:%s" %(host, port))
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self._remote_addr = (host, port)
        asyncore.dispatcher.connect(self, self._remote_addr)

    def shutdown(self):
        """
        Shutdown the bridge.

        All messages already in the out_queue will first be sent. But new
        messages added after the shutdown will not be sent.

        """
        log.info("OANBridge:shutdown")
        self.out_queue.put(None)

    #
    # Internal asyncore events.
    #

    def handle_connect(self):
        """
        Event called by asyncore when a connection has been established.

        The connection was initialized from the connect function. That means
        the bridge instance did connect to a remote host with success and
        didn't answer on a connection from a remote host.

        CALLBACK - called from this method
            connect_callback(bridge)

        """
        log.info("OANBridge:handle_connect, total connections: [%s]" %
                 len(asyncore.socket_map))
        self.connect_callback(self)

    def handle_close(self):
        """
        Event called by asyncore when a connection has been closed.

        CALLBACK - called from this method
            close_callback(bridge)

        """
        log.info("OANBridge:handle_close")
        self.close()
        if self.node:
            self.node.update(state = OANNetworkNodeState.DISCONNECTED)
        self.close_callback(self)

    def readable(self):
        """
        Is the bridge ready to read messages/data from remote host.

        Called by asyncore to verify that asyncore can call handle_read.

        """
        return True

    def writable(self):
        """
        Does the bridge have any messages/data to send to remote host.

        Called by asyncore to verify that asyncore can call handle_write.

        """
        self._shutdown_if_idle()

        is_empty_queue = (self.out_queue is None or self.out_queue.empty())
        is_empty_buffer = len(self._out_buffer) == 0
        is_writable = (not is_empty_buffer or not is_empty_queue)

        log.info("OANBridge:writable is_writable: [%s]" % is_writable)

        return is_writable

    def handle_read(self):
        """
        Event called by asyncore when it's time to read from the socket.

        CALLBACK - called from this method
            received_callback(bridge, message)
                Called when a full message has been received.

        """
        log.info("OANBridge:handle_read")
        data = self.recv(1024)
        if self.node:
            log.info("OANBridge:handle_read IN[%s][%s]" % (
                self.node.oan_id, data))

        if data:
            self.in_buffer += data

            pos = self.in_buffer.find('\n')
            while pos > -1:
                cmd = self.in_buffer[:pos]
                self.in_buffer = self.in_buffer[pos+1:]

                log.info("OANBridge:handle_read CMD[%s]" % cmd)
                message = self._read_message(cmd)
                self.received_callback(self, message)
                pos = self.in_buffer.find('\n')

    def handle_write(self):
        """
        Event called by asyncore when it's time to write to the socket.

        """
        if (len(self._out_buffer) == 0):
            if self.out_queue and not self.out_queue.empty():
                message = self.out_queue.get()

                if (message == None):
                    log.info("OANBridge:handle_write closing")
                    self.handle_close()
                    return

                cmd = self._send_message(message)
                log.info("OANBridge:handle_write CMD[%s]" % cmd)
                self._out_buffer = cmd

        sent = self.send(self._out_buffer)
        if self.node:
            log.info("OANBridge:handle_write OUT[%s][%s]" % (
                     self.node.oan_id, self._out_buffer[:sent]))

        self._out_buffer = self._out_buffer[sent:]

    def handle_error(self):
        """
        Handle all errors and exceptions that will ocure in the bridge and
        it's callbacks.

        """
        log.info("OANBridge:handle_error")

        exc_type, exc_value, exc_traceback = sys.exc_info()
        tb = traceback.format_exception(exc_type, exc_value, exc_traceback)
        tb = ([txt.replace("\\n", "\n") for txt in tb])
        txt = "".join(tb)
        log.info("OANBridge:handle_error: remote_host%s, %s, %s\n%s" %
                 (self._remote_addr, exc_type, exc_value, txt))

        self.handle_close()

    def _read_message(self, raw_message):
        """
        Creates/decodes a message object from a string.

        """
        message = decode(raw_message.strip())
        log.info("OANBridge:_read_message: %s" % message.__class__.__name__)

        if self.node:
            log.info("OANBridge:_read_message: %s from %s" % (
                     message.__class__.__name__, self.node.oan_id))
            self.node.add_message_statistic(
                message.__class__.__name__, in_time = True)
            self.node.touch()

        return message

    def _send_message(self, message):
        """
        Creates/encodes a string from a message object.

        """
        log.info("OANBridge:_send_message: %s" % message.__class__.__name__)

        raw_message = encode(message)
        if self.node:
            log.info("OANBridge:_send_message: %s to %s" % (message.__class__.__name__, self.node.oan_id))
            self.node.add_message_statistic(message.__class__.__name__, out_time = True)

        return raw_message + '\n'

    def _shutdown_if_idle(self):
        """
        Shutdown the bridge if no data has been read or written for X seconds.

        """
        if self.node:
            if self.node.has_heartbeat_state(OANHeartbeat.IDLE):
                log.info("OANBridge:writable idling")
                self.shutdown()


    # def got_handshake(self, message):
    #     # Update with external ip. Sending node is only aware of internal ip,
    #     # firewall might MASQ/NAT to extetnal ip.
    #     message.host = self._remote_addr[0]
    #     #self.node = g().get(message)
    #     #self.node.update(state = OANNetworkNodeState.CONNECTED)
    #     self.out_queue = self.node.out_queue
