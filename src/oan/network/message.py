#!/usr/bin/env python
'''


'''

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import socket
from oan.util import log


class NetworksMessageConnectToNode:
    @classmethod
    def create(cls, node):
        obj = cls()
        obj.node = node
        return obj

    def execute(self, server):
        log.debug("NetworksMessageConnectToNode: %s, node: %s" % (server, self.node.oan_id))
        if self.node.is_disconnected():
            server.connect_to_node(self.node)


'''


'''
class OANNetworkMessageListen:
    port = None

    @classmethod
    def create(cls, port):
        obj = cls()
        obj.port = port
        return obj

    def execute(self, server):
        log.info("OANNetworkMessageListen")
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        host = s.getsockname()[0]
        s.close()

        server.listen(host, int(self.port))


'''

'''
class OANNetworkMessageConnectOan:
    host = None
    port = None

    @classmethod
    def create(cls, host, port):
        obj = cls()
        obj.host = host
        obj.port = port
        return obj

    def execute(self, server):
        log.info("OANNetworkMessageConnectOan")
        server.connect_to_oan(self.host, self.port)


'''

'''
class OANNetworkMessageShutdown:
    def execute(self, server):
        pass

