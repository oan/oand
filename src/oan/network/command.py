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


class NetworksCommandConnectToNode:
    @classmethod
    def create(cls, node):
        obj = cls()
        obj.node = node
        return obj

    def execute(self, server):
        log.debug("NetworksCommandConnectToNode:execute: %s, node: %s" % (server, self.node.oan_id))
        if self.node.is_disconnected():
            server.connect_to_node(self.node)


class OANNetworkCommandListen:
    port = None

    @classmethod
    def create(cls, port):
        obj = cls()
        obj.port = port
        return obj

    def execute(self, server):
        log.info("OANNetworkCommandListen:execute")
        host = get_local_host()
        server.listen(host, int(self.port))


class OANNetworkCommandConnectOan:
    host = None
    port = None

    @classmethod
    def create(cls, host, port):
        obj = cls()
        obj.host = host
        obj.port = port
        return obj

    def execute(self, server):
        print "connect_to_oan %s:%d" % (self.host, self.port)
        log.info("OANNetworkCommandConnectOan:execute")
        server.connect_to_oan(self.host, self.port)

