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
from oan_bridge import OANBridge
from oan_loop import OANLoop
from oan_event import OANEvent

class OANServer(asyncore.dispatcher):
    node_id = None
    bridges = {}

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


    def __init__(self, node_id, host, port):
        asyncore.dispatcher.__init__(self)
        self.node_id = node_id
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def add_bridge(self, bridge):
        print "OanServer:add_bridge"
        if (bridge.connected_to not in self.bridges):
            self.bridges[bridge.connected_to] = bridge
            self.on_bridge_added(bridge)

    def remove_bridge(self, bridge):
        print "OanServer:remove_bridge"
        if (bridge.connected_to in self.bridges):
            del self.bridges[bridge.connected_to]
            self.on_bridge_removed(bridge)

    def idle_bridge(self, bridge):
        print "OanServer:idle_bridge"
        if (bridge.connected_to in self.bridges):
            self.on_bridge_idle(bridge)

    def connect_to_node(self, host, port):
        bridge = OANBridge(self)
        bridge.server = self
        bridge.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        bridge.connect( (host, port) )

        print "OanServer:connect_to_node %s:%d" % (host, port)

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
            bridge.server = self
            bridge.handshake()

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
    print "my_bridge_added connected to %s" % (bridge.connected_to)
    if (bridge.connected_to == 'c1'):
        bridge.out_queue.put("Welcome message from [%s]" % bridge.server.node_id);

def my_bridge_removed(bridge):
    print "my_bridge_removed"

def main():
    server = OANServer('s1','localhost', 8002)
    server.on_bridge_added += (my_bridge_added, )

    loop = OANLoop()
    loop.on_shutdown += (server.shutdown, )
    loop.start()

    try:
        while True:
            time.sleep(10)
            if ('c1' in server.bridges):
                server.bridges['c1'].out_queue.put("clock [%s] from [%s]" % (datetime.datetime.now(), server.node_id))

    except KeyboardInterrupt:
        pass

    finally:
        loop.stop()


if __name__ == "__main__":
    main()
