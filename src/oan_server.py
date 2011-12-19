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
from oan_simple_node_manager import OANNode, OANNodeManager
from oan_message import OANMessagePing

class OANServer(asyncore.dispatcher):
    node = None #my own node
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


    def __init__(self, node):
        asyncore.dispatcher.__init__(self)
        self.node = node
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((node.host, node.port))
        self.listen(5)

    def add_bridge(self, bridge):
        print "OanServer:add_bridge"
        if (bridge.node.node_id not in self.bridges):
            self.bridges[bridge.node.node_id] = bridge
            self.on_bridge_added(bridge)

    def remove_bridge(self, bridge):
        print "OanServer:remove_bridge"
        if (bridge.node.node_id in self.bridges):
            del self.bridges[bridge.node.node_id]
            self.on_bridge_removed(bridge)

    def idle_bridge(self, bridge):
        #print "OanServer:idle_bridge"
        if (bridge.node.node_id in self.bridges):
            self.on_bridge_idle(bridge)


    def connect_to_node(self, node):
        bridge = OANBridge(self)
        bridge.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        bridge.connect( (node.host, node.port) )
        print "OanServer:connect_to_node %s:%d:%s" % (node.host, node.port, bridge.connected)
        return bridge.connected

    def handle_connect(self):
        print "OanServer:handle_connect"
        self.handle_connect()

    def handle_accept(self):
        print "OanServer:handle_accept"
        pair = self.accept()
        if pair is None:
            pass
        else:
            sock, addr = pair
            print 'OanServer: incoming connection from %s' % repr(addr)
            bridge = OANBridge(self, sock)
            bridge.send_handshake()

    def handle_close(self):
        print "OanServer:handle_close"
        self.close()

    def shutdown(self):
        self.close()
        for k, bridge in self.bridges.iteritems():
            bridge.shutdown()

    def handle_error(self):
        print "OanServer:handle_error"
        asyncore.dispatcher.handle_error(self)


def my_bridge_added(bridge):
    print "my_bridge_added connected to %s" % (bridge.node.node_id)
    #if (bridge.node.node_id == 'n2'):
    #    bridge.out_queue.put("Welcome message from [%s]" % bridge.server.node_id);

def my_bridge_removed(bridge):
    print "my_bridge_removed"

def my_bridge_idle(bridge):
    pass
    #print "my_bridge_idle"
    #bridge.shutdown()

def main():

    n2_node = OANNode('n2', 'localhost', 8002)
    n2_server = OANServer(n2_node)

    n1_node = OANNode('n1', 'localhost', 8001) # remote

    manager = OANNodeManager(n2_server)
    oan.set_managers("None", "None", manager)
    manager.add_node(n1_node)
    manager.add_node(n2_node)

    n2_server.on_bridge_added += (my_bridge_added, )
    n2_server.on_bridge_removed += (my_bridge_removed, )
    n2_server.on_bridge_idle += (my_bridge_idle, )

    loop = OANLoop()
    loop.on_shutdown += (n2_server.shutdown, )
    loop.start()

    try:
        while True:
            manager.send('n1', OANMessagePing.create('n1'))
            time.sleep(5)

    except KeyboardInterrupt:
        pass

    finally:
        loop.stop()

if __name__ == "__main__":
    main()

