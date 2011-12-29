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
from oan_bridge import OANBridge
from oan_loop import OANLoop
from oan_event import OANEvent
from oan_node_manager import OANNetworkNode, OANNetworkNodeState, OANNodeManager
from oan_message import OANMessagePing

# make OANServer.connect_to_node thread safe alternative OANNodeManager
class OANServer(asyncore.dispatcher):

    bridges = {} #bridges to other nodes

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


    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        queue = Queue()
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)


    def add_bridge(self, bridge):
        print "OanServer:add_bridge"
        bridge.node.state = OANNetworkNodeState.connected
        self.bridges[bridge.node.uuid] = bridge
        self.on_bridge_added(bridge)

    def remove_bridge(self, bridge):
        print "OanServer:remove_bridge"
        if (bridge.node.uuid in self.bridges):
            bridge.node.state = OANNetworkNodeState.disconnected
            del self.bridges[bridge.node.uuid]
            self.on_bridge_removed(bridge)

    def idle_bridge(self, bridge):
        #print "OanServer:idle_bridge"
        if (bridge.node.uuid in self.bridges):
            self.on_bridge_idle(bridge)

    def connect_to_node(self, node):

        # lock
        if node.state == OANNetworkNodeState.disconnected:
            node.state = OANNetworkNodeState.connecting
            bridge = OANBridge(self)
            bridge.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            bridge.connect( (node.host, node.port) )
            #print "OanServer:connect_to_node %s:%d:%s" % (node.host, node.port, bridge.connected)
        # ----


    def handle_accept(self):
        print "OanServer:handle_accept"
        pair = self.accept()
        if pair is None:
            pass
        else:
            sock, addr = pair
            print 'OanServer: accepting connection from %s' % repr(addr)
            bridge = OANBridge(self, sock)
            bridge.handle_accept()

    def handle_close(self):
        print "OanServer:handle_close"
        self.close()

    def shutdown(self):
        self.close()
        for k, bridge in self._map.iteritems():
            bridge.shutdown()

    def handle_error(self):
        print "OanServer:handle_error"
        asyncore.dispatcher.handle_error(self)


def my_bridge_added(bridge):
    print "my_bridge_added connected to %s" % (bridge.node.uuid)

def my_bridge_removed(bridge):
    print "my_bridge_removed"

def my_bridge_idle(bridge):
    print "my_bridge_idle"
    #bridge.shutdown()

def main():
    pass

if __name__ == "__main__":
    main()

