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
import time
import datetime
import thread
from Queue import Queue
from threading import Thread

import oan
from oan.util import log
from bridge import OANBridge
from oan.event import OANEvent
from oan.network.network_node import OANNetworkNodeState



class OANListen(asyncore.dispatcher):
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)
        log.info("Start listening on %s:%d" % (host, port))



    def handle_accept(self):
        #print "OanServer:handle_accept"
        pair = self.accept()
        if pair is None:
            pass
        else:
            try:
                sock, addr = pair
                log.info('OanServer: accepting connection from %s' % repr(addr))
                bridge = OANBridge(self, sock)
                bridge.remote_addr = addr
                bridge.handle_accept()
            except Exception, e:
                log.info('OanServer: invalid peer connected from %s [%s]' % (repr(addr), e))

    def handle_close(self):
        log.info("OanServer:handle_close")
        self.close()



    def handle_error(self):
        log.info("OanServer:handle_error")
        asyncore.dispatcher.handle_error(self)




# make OANServer.connect_to_node thread safe alternative OANNodeManager
class OANServer(object):

    bridges = {} #bridges to other nodes

    _listen = None

    '''
        use:
        def my_bridge_added(bridge)
            pass

        loop.on_bridge_added += (my_bridge_added, )
    '''
    on_bridge_added = OANEvent()

    '''
        use:
        def on_bridge_removed(bridge)
            pass

        loop.on_bridge_removed += (on_bridge_removed, )
    '''
    on_bridge_removed = OANEvent()


    '''
        use:
        def on_bridge_idle(bridge)
            pass

        loop.on_bridge_idle += (on_bridge_idle, )
    '''
    on_bridge_idle = OANEvent()

    def add_bridge(self, bridge):
        #print "OanServer:add_bridge"
        bridge.node.state = OANNetworkNodeState.connected
        self.bridges[bridge.node.oan_id] = bridge
        self.on_bridge_added(bridge)

    def remove_bridge(self, bridge):
        #print "OanServer:remove_bridge"
        if (bridge.node.oan_id in self.bridges):
            bridge.node.state = OANNetworkNodeState.disconnected
            del self.bridges[bridge.node.oan_id]
            self.on_bridge_removed(bridge)

    def idle_bridge(self, bridge):
        #print "OanServer:idle_bridge"
        if (bridge.node.oan_id in self.bridges):
            self.on_bridge_idle(bridge)


    def connect_to_node(self, node):
        log.info("Connect to %s:%s" % (node.host, node.port))
        node.state = OANNetworkNodeState.connecting
        bridge = OANBridge(self)
        bridge.connect(node.host, node.port)

    def connect_to_oan(self, host, port):
        log.info("OanServer:connect_to_oan %s:%d" % (host, port))
        bridge = OANBridge(self)
        bridge.connect(host, port)

    def listen(self, host, port):
        self._listen = OANListen(host, port)



    def shutdown(self):
        if self._listen and self._listen.accepting:
            self._listen.close()

        for bridge in self.bridges.values():
            bridge.shutdown()

        # check if there any sockets left with no handshake
        # for bridge in self._map.values():
        #     bridge.handle_close()

