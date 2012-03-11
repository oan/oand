#!/usr/bin/env python
"""
RPC server handling request from oan clients.

"""

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import asyncore
import socket

from oan.util import log
from bridge import OANBridge


class OANListen(asyncore.dispatcher):
    """
    Listens for new socket connections.

    Used together with asyncore.loop() in OANNetworkWorker.

    CALLBACKS

    accept_callback(bridge)
        Called when a connection has been established, that was initialized
        from the remote host.

    """

    # Callbacks
    accept_callback = None

    # All connected bridges
    # @TODO: Either handle connected bridges elsewere or remove bridges from
    #        this list when they are closed.
    _bridges = []

    def __init__(self, host, port, accept_callback):
        asyncore.dispatcher.__init__(self)
        self.accept_callback = accept_callback

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)
        log.info("Start listening on %s:%d" % (host, port))

    def handle_accept(self):
        """
        Create a new OANBridge to remote node when a connection is accepted.

        """
        log.info("OANListen:handle_accept")
        try:
            pair = self.accept()
            if pair is None:
                return

            sock, addr = pair
            log.info('OANListen: accepting connection from %s' % repr(addr))
            bridge = OANBridge(sock)
            bridge.remote_addr = addr
            self.accept_callback(bridge)
            self._bridges.append(bridge)

        except Exception, e:
            log.info('OANListen: invalid peer connected from %s [%s]' %
                     (repr(addr), e))

    def handle_close(self):
        log.info("OANListen:handle_close")
        [bridge.shutdown() for bridge in self._bridges]
        self.close()

    def handle_error(self):
        log.info("OANListen:handle_error")
        asyncore.dispatcher.handle_error(self)
