#!/usr/bin/env python
"""

"""
__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from oan.util import log
from oan.util.network import get_local_host
from oan.network.network_node import OANNetworkNodeState
from oan.network.bridge import OANBridge
from oan.network.server import OANListen

class NetworksCommandConnectToNode:
    @classmethod
    def create(cls, node):
        obj = cls()
        obj.node = node
        return obj

    def execute(self):
        log.debug("NetworksCommandConnectToNode:execute: %s" % (self.node.oan_id))
        if self.node.is_disconnected():
            (name, host, port, state, blocked, heartbeat) = self.node.get()
            log.info("Connect to %s:%s" % (host, port))
            self.node.update(state = OANNetworkNodeState.CONNECTING)
            bridge = OANBridge(self)
            bridge.connect(host, port)

class OANNetworkCommandListen:
    port = None

    @classmethod
    def create(cls, port):
        obj = cls()
        obj.port = port
        return obj

    def execute(self):
        log.info("OANNetworkCommandListen:execute")
        host = get_local_host()
        OANListen(self, host, self.port)


class OANNetworkCommandConnectOan:
    host = None
    port = None

    @classmethod
    def create(cls, host, port):
        obj = cls()
        obj.host = host
        obj.port = port
        return obj

    def execute(self):
        print "connect_to_oan %s:%d" % (self.host, self.port)
        log.info("OANNetworkCommandConnectOan:execute")
        bridge = OANBridge(self)
        bridge.connect(self.host, self.port)

