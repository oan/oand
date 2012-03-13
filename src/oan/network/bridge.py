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
from oan.network import serializer
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

    error_callback(bridge, exc_type, exc_value)
        Called when an error has occured.

    """
    # Callbacks
    connect_callback = None
    received_callback = None
    close_callback = None
    error_callback = None

    # Messages that should be sent to remote host.
    out_queue = None

    # Remote host that the bridge is connected to.
    node = None

    # Tuple of host and port to remote host.
    _remote_addr = None

    #
    _auth = None

    _is_auth = None

    # Buffer of data to send to remote host.
    _out_buffer = ''

    # Buffer of data received from remote host.
    _in_buffer = ''

    def __init__(self, host, port, auth, sock = None):
        asyncore.dispatcher.__init__(self, sock)
        self._remote_addr = (host, port)
        self._auth = auth
        self._is_auth = False
        self.connect_callback = lambda bridge, auth : None
        self.received_callback = lambda bridge, msg : None
        self.close_callback = lambda bridge : None
        self.error_callback = lambda bridge, exc_type, exc_value: None

    def connect(self):
        """
        Connect to a remote host and establish the bridge.

        """
        log.info("OANBridge:connect %s" % repr(self._remote_addr))
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        asyncore.dispatcher.connect(self, self._remote_addr)

    def shutdown(self):
        """
        Shutdown the bridge.

        All messages already in the out_queue will first be sent. But new
        messages added after the shutdown will not be sent.

        """
        log.info("OANBridge:shutdown")
        self.out_queue.put(None)

    def send_handshake(self):
        cmd = self._send_message(self._auth)
        log.info("OANBridge:send_handshake CMD[%s]" % cmd)
        self._out_buffer = cmd

    #
    # Internal asyncore events.
    #

    def handle_connect(self):
        """
        Event called by asyncore when a connection has been established.

        The connection was initialized from the connect function. That means
        the bridge instance did connect to a remote host with success and
        didn't answer on a connection from a remote host.

        """
        log.info("OANBridge:handle_connect, total connections: [%s]" %
                 len(asyncore.socket_map))
        self.send_handshake()

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
            self._in_buffer += data

            pos = self._in_buffer.find('\n')
            while pos > -1:
                cmd = self._in_buffer[:pos]
                self._in_buffer = self._in_buffer[pos+1:]

                log.info("OANBridge:handle_read CMD[%s]" % cmd)
                message = self._read_message(cmd)
                if self._is_auth:
                    self.received_callback(self, message)
                else:
                    self._handle_handshake(message)

                pos = self._in_buffer.find('\n')

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

        CALLBACK - called from this method
            error_callback(bridge, exc_type, exc_value)
                Called when a error has occured.

        """
        exc_type, exc_value, exc_traceback = sys.exc_info()
        if (exc_type is socket.error):
            txt = ""
        else:
            tb = traceback.format_exception(exc_type, exc_value, exc_traceback)
            tb = ([txt.replace("\\n", "\n") for txt in tb])
            txt = "\n" + "".join(tb)

        log.info("OANBridge:handle_error: remote_host%s, %s, %s%s" %
                 (self._remote_addr, exc_type, exc_value, txt))

        self.error_callback(self, exc_type, exc_value)
        self.handle_close()

    def _read_message(self, raw_message):
        """
        Creates/decodes a message object from a string.

        CALLBACK - called from this method
            connect_callback(bridge)
                called when a handshake message is received.

        """
        message = serializer.decode(raw_message.strip())
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

        raw_message = serializer.encode(message)
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

    def _handle_handshake(self, auth):
        # Update with external ip. Sending node is only aware of internal ip,
        # firewall might MASQ/NAT to extetnal ip.
        if not isinstance(auth, OANBridgeAuth):
            log.info("OANBridge:_handle_handshake expected auth %s" %
                     auth.__class__.__name__)
            self.handle_close()
            return

        if auth.version != self._auth.version:
            log.info("OANBridge:_handle_handshake invalid version %s!=%s" %
                     (auth.version, self._auth.version))
            self.handle_close()
            return

        self._is_auth = True

        auth.host = self._remote_addr[0]
        self.connect_callback(self, auth)


class OANBridgeAuth():
    version = None
    oan_id = None
    host = None
    port = None
    blocked = None
    ttl = False

    @classmethod
    def create(cls, version, oan_id, host, port, blocked):
        obj = cls()
        obj.version = version
        obj.oan_id = str(oan_id)
        obj.host = host
        obj.port = port
        obj.blocked = blocked

        log.info("OANBridgeAuth:__init__ %s %s:%s blocked: %s" % (
            obj.oan_id, obj.host, obj.port, obj.blocked))

        return obj

serializer.add(OANBridgeAuth)
