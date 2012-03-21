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

class OANBridge(asyncore.dispatcher):
    """
    A network bridge used to send messages between two nodes.

    CALLBACKS

    connect_callback(bridge)
        Called when a connection has been established, that was initialized
        from this host.

    message_callback(bridge, message)
        Called when a message has been received from a remote host.

    close_callback(bridge)
        Called when the connection has closed.

    error_callback(bridge, exc_type, exc_value)
        Called when an error has occured.

    """
    # Callbacks
    connect_callback = None
    message_callback = None
    close_callback = None
    error_callback = None

    # Remote host that the bridge is connected to.
    node = None

    # Tuple of host and port to remote host.
    _remote_addr = None

    #
    _auth = None

    # Buffer of data to send to remote host.
    _out_buffer = ''

    # Buffer of data received from remote host.
    _in_buffer = ''

    # got close message from remote host.
    _closing = None

    def __init__(self, host, port, auth, sock = None):
        asyncore.dispatcher.__init__(self, sock)
        self._remote_addr = (host, port)
        self._auth = auth
        self._closing = False

        self.connect_callback = lambda bridge, auth : None
        self.message_callback = lambda bridge, msg : None
        self.close_callback = lambda bridge : None
        self.error_callback = lambda bridge, exc_type, exc_value: None

    def connect(self):
        """
        Connect to a remote host and establish the bridge.

        """
        log.info("OANBridge:connect %s" % repr(self._remote_addr))
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        asyncore.dispatcher.connect(self, self._remote_addr)


    def send(self, messages):
        encoded_messages = []
        for message in messages:
            encoded_messages.append(self._encode_message(message))

        self._out_buffer += ''.join(encoded_messages)

    def handshake(self):
        log.info("OANBridge:handshake %s" % repr(self._remote_addr))
        self._out_buffer += self._encode_message(self._auth)

    def shutdown(self):
        log.info("OANBridge:shutdown %s" % repr(self._remote_addr))
        self._out_buffer += self._encode_message(OANBridgeClose.create())

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

        self.handshake()

    def handle_close(self):
        """
        Event called by asyncore when a connection has been closed.

        CALLBACK - called from this method
            close_callback(bridge)

        """
        log.info("OANBridge:handle_close")
        self.close()
        self.close_callback(self)

    def readable(self):
        """
        Is the bridge ready to read messages/data from remote host.

        Called by asyncore to verify that asyncore can call handle_read.

        """
        is_readable = not self._closing
        log.info("OANBridge %s: readable: [%s]" % (repr(self._remote_addr), is_readable))
        return is_readable

    def writable(self):
        """
        Does the bridge have any messages/data to send to remote host.

        Called by asyncore to verify that asyncore can call handle_write.

        """

        is_writable = len(self._out_buffer) > 0
        log.info("OANBridge %s: writable: [%s]" % (repr(self._remote_addr), is_writable))
        return is_writable

    def handle_read(self):
        """
        Event called by asyncore when it's time to read from the socket.

        CALLBACK - called from this method
            message_callback(bridge, message)
                Called when a full message has been received.

        """
        log.info("OANBridge:handle_read")
        data = self.recv(1024)
        if self.node:
            log.info("OANBridge:handle_read IN[%s][%s]" % (
                self.node.oan_id, data))

        if data:
            self._read_state = 2
            self._in_buffer += data

            pos = self._in_buffer.find('\n')
            while pos > -1:
                cmd = self._in_buffer[:pos]
                self._in_buffer = self._in_buffer[pos+1:]

                log.info("OANBridge:handle_read CMD[%s]" % cmd)
                message = self._decode_message(cmd)
                if isinstance(message, OANBridgeAuth):
                    self._auth_message(message)
                elif isinstance(message, OANBridgeClose):
                    self._close_message(message)
                else:
                    self.message_callback(self, message)

                pos = self._in_buffer.find('\n')

    def handle_write(self):
        """
        Event called by asyncore when it's time to write to the socket.

        """
        sent = asyncore.dispatcher.send(self, self._out_buffer)
        if self.node:
            log.info("OANBridge:handle_write OUT[%s][%s]" % (
                     self.node.oan_id, self._out_buffer[:sent]))

        self._out_buffer = self._out_buffer[sent:]
        self._check_close()

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

    def _decode_message(self, raw_message):
        """
        Creates/decodes a message object from a string.

        CALLBACK - called from this method
            connect_callback(bridge)
                called when a handshake message is received.

        """
        message = serializer.decode(raw_message.strip())
        log.info("OANBridge:_decode_message: %s" % message.__class__.__name__)

        if self.node:
            log.info("OANBridge:_decode_message: %s from %s" % (
                     message.__class__.__name__, self.node.oan_id))
            self.node.add_message_statistic(
                message.__class__.__name__, in_time = True)
            self.node.touch()

        return message

    def _encode_message(self, message):
        """
        Creates/encodes a string from a message object.

        """
        log.info("OANBridge:_encode_message: %s" % message.__class__.__name__)

        raw_message = serializer.encode(message)
        if self.node:
            log.info("OANBridge:_encode_message: %s to %s" % (message.__class__.__name__, self.node.oan_id))
            self.node.add_message_statistic(message.__class__.__name__, out_time = True)

        return raw_message + '\n'


    def _close_message(self, close):
        log.info("OANBridge:_close_message")
        self._closing = True
        self._check_close()

    def _auth_message(self, auth):
        # Update with external ip. Sending node is only aware of internal ip,
        # firewall might MASQ/NAT to extetnal ip.

        if auth.version != self._auth.version:
            log.info("OANBridge:_auth_message invalid version %s!=%s" %
                     (auth.version, self._auth.version))
            self.handle_close()
            return

        log.info("OANBridge:_auth_message handshake accepted")
        auth.host = self._remote_addr[0]
        self.connect_callback(self, auth)

    def _check_close(self):
        if self._closing and not self.writable():
            log.info("OANBridge:_close_message is closing")
            self.handle_close()

class OANBridgeAuth():
    version = None
    oan_id = None
    host = None
    port = None
    blocked = None

    @classmethod
    def create(cls, version, oan_id, host, port, blocked):
        obj = cls()
        obj.version = version
        obj.oan_id = str(oan_id)
        obj.host = host
        obj.port = port
        obj.blocked = blocked

        log.info("OANBridgeAuth: %s %s:%s blocked: %s" % (
            obj.oan_id, obj.host, obj.port, obj.blocked))

        return obj

class OANBridgeClose():

    @classmethod
    def create(cls):
        obj = cls()
        log.info("OANBridgeClose")
        return obj


serializer.add(OANBridgeAuth)
serializer.add(OANBridgeClose)
