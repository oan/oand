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
from oan.async.network_node import OANNetworkNodeState
from oan.async.network import OANNetworkServer

class NetworksCommandConnectToNode:
    _auth = None
    _node = None

    @classmethod
    def create(cls, node, auth):
        obj = cls()
        obj._auth = auth
        obj._node = node
        return obj

    def execute(self):
        log.debug("NetworksCommandConnectToNode:execute: %s" % (self._node.oan_id))
        if self._node.is_disconnected():
            (name, host, port, state, blocked, heartbeat) = self._node.get()
            log.info("Connect to %s:%s" % (host, port))
            self._node.update(state = OANNetworkNodeState.CONNECTING)
            OANNetworkServer.connect(host, port, self._auth)

class OANNetworkCommandListen:
    _auth = None

    @classmethod
    def create(cls, auth):
        obj = cls()
        obj._auth = auth
        return obj

    def execute(self):
        log.info("OANNetworkCommandListen:execute")
        OANNetworkServer.listen(self._auth)

class OANNetworkCommandConnectOan:
    _host = None
    _port = None
    _auth = None

    @classmethod
    def create(cls, host, port, auth):
        obj = cls()
        obj._host = host
        obj._port = port
        obj._auth = auth

        return obj

    def execute(self):
        print "connect_to_oan %s:%d" % (self._host, self._port)
        log.info("OANNetworkCommandConnectOan:execute")
        OANNetworkServer.connect(self._host, self._port, self._auth)
