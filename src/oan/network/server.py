#!/usr/bin/env python
'''
RPC server handling request from oan clients.

'''

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
from oan.event import OANEvent
from oan.network.network_node import OANNetworkNodeState


class OANListen(asyncore.dispatcher):
    """
    Listens for new socket connections.

    Uses together with asyncore.loop() in OANNetworkWorker.

    """
    def __init__(self, server, host, port):
        asyncore.dispatcher.__init__(self)

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)
        self.server = server
        log.info("Start listening on %s:%d" % (host, port))

    def handle_accept(self):
        """
        Create a new OANBridge to remote node when a connection is accepted.

        """
        log.debug("OANListen:handle_accept")
        try:
            pair = self.accept()
            if pair is None:
                return

            sock, addr = pair
            log.info('OANListen: accepting connection from %s' % repr(addr))
            bridge = OANBridge(self.server, sock)
            bridge.remote_addr = addr
            bridge.handle_accept()
        except Exception, e:
            log.info('OANListen: invalid peer connected from %s [%s]' % (repr(addr), e))

    def handle_close(self):
        log.info("OANListen:handle_close")
        self.close()

    def handle_error(self):
        log.info("OANListen:handle_error")
        asyncore.dispatcher.handle_error(self)


class OANServer(object):
    """


    TODO: Make OANServer.connect_to_node thread safe alternative OANNodeManager

    EVENTS:

    on_bridge_added
        Callback event that will be triggered when a bridge is added
        to the server.

        Example:
        def my_bridge_added(bridge)
            pass

        server.on_bridge_added.append(my_bridge_added)

    on_bridge_removed
        Callback event that will be triggered when a bridge is removed
        from the server.

        Example:
        def my_bridge_removed(bridge)
            pass

        server.on_bridge_removed.append(my_bridge_removed)

    on_bridge_removed
        Callback event that will be triggered when the bridge is idling.

        Example:
        def my_bridge_idle(bridge)
            pass

        server.on_bridge_idle.append(my_bridge_idle)

    """
    # Events
    on_bridge_added = OANEvent()
    on_bridge_removed = OANEvent()
    on_bridge_idle = OANEvent()

    # Private variables

    # Bridges to other nodes
    bridges = {}

    _listen = None

    def add_bridge(self, bridge):
        log.debug("OanServer:add_bridge")
        bridge.node.update(state = OANNetworkNodeState.CONNECTED)
        self.bridges[bridge.node.oan_id] = bridge
        self.on_bridge_added(bridge)

    def remove_bridge(self, bridge):
        log.debug("OanServer:remove_bridge")
        if (bridge.node.oan_id in self.bridges):
            bridge.node.update(state = OANNetworkNodeState.DISCONNECTED)
            del self.bridges[bridge.node.oan_id]
            self.on_bridge_removed(bridge)

    def idle_bridge(self, bridge):
        log.debug("OanServer:idle_bridge")
        if (bridge.node.oan_id in self.bridges):
            self.on_bridge_idle(bridge)

    def connect_to_node(self, node):
        (name, host, port, state, blocked, heartbeat) = node.get()
        log.info("Connect to %s:%s" % (host, port))
        node.update(state = OANNetworkNodeState.CONNECTING)
        bridge = OANBridge(self)
        bridge.connect(host, port)

    def connect_to_oan(self, host, port):
        log.info("OanServer:connect_to_oan %s:%d" % (host, port))
        bridge = OANBridge(self)
        bridge.connect(host, port)

    def listen(self, host, port):
        self._listen = OANListen(self, host, port)

    def shutdown(self):
        if self._listen and self._listen.accepting:
            self._listen.close()

        for bridge in self.bridges.values():
            bridge.shutdown()

        # check if there any sockets left with no handshake
        # for bridge in self._map.values():
        #     bridge.handle_close()

