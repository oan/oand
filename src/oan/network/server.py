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

import sys
import traceback
import asyncore
import socket

from oan.util import log
from bridge import OANBridge


class OANListen(asyncore.dispatcher):
    """
    Listens for new socket connections.

    Used together with asyncore.loop() in OANNetworkWorker.

    The OANListen instance don't need to be shutdown/closed manually, that
    is done when the asyncore.loop dies.

    CALLBACKS

    accept_callback(bridge)
        Called when a connection has been established, that was initialized
        from the remote host.

    """

    _auth = None

    # Callbacks
    accept_callback = None

    def __init__(self, host, port, auth, accept_callback):
        asyncore.dispatcher.__init__(self)
        self._auth = auth
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
            host, port = addr
            log.info('OANListen: accepting connection from %s' % repr(addr))
            bridge = OANBridge(host, port, self._auth, sock)
            bridge.send_handshake()
            self.accept_callback(bridge)

        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb = traceback.format_exception(exc_type, exc_value, exc_traceback)
            tb = ([txt.replace("\\n", "\n") for txt in tb])
            txt = "\n" + "".join(tb)

            log.info("OANListen:handle_accept: remote_host%s, %s, %s%s" %
                     (repr(addr), exc_type, exc_value, txt))

    def handle_error(self):
        log.info("OANListen:handle_error")
        asyncore.dispatcher.handle_error(self)
