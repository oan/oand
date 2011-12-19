#!/usr/bin/env python
'''
RPC client.

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
from threading import Thread
from threading import Timer
from Queue import Queue

from oan_simple_node_manager import OANNode, OANNodeManager
from oan_server import OANServer
from oan_loop import OANLoop

def my_bridge_added(bridge):
    print "my_bridge_added connected to %s" % (bridge.node.node_id)
    if (bridge.node.node_id == 's1'):
        bridge.out_queue.put("Welcome message from [%s]" % bridge.server.node_id);

def my_bridge_removed(bridge):
    print "my_bridge_removed"

def my_bridge_idle(bridge):
    pass
    #print "my_bridge_idle"
    #bridge.shutdown()

def main():

    server_node = OANNode('s1', 'localhost', 8001)
    client_node = OANNode('c1', 'localhost', 8002)
    server = OANServer(client_node)

    manager = OANNodeManager(server)
    manager.add_node(server_node)
    manager.add_node(client_node)

    manager.send('s1', 'my super cool queue message before connection')
    manager.start()

    server.on_bridge_added += (my_bridge_added, )
    server.on_bridge_removed += (my_bridge_removed, )
    server.on_bridge_idle += (my_bridge_idle, )

    loop = OANLoop()
    loop.on_shutdown += (server.shutdown, )
    loop.start()

    try:
        while True:
            time.sleep(5)
            if ('s1' in server.bridges):
                manager.send('s1', ("clock [%s] from [%s]" % (datetime.datetime.now(), server.node.node_id)))

    except KeyboardInterrupt:
        pass

    finally:
        manager.stop()
        loop.stop()

if __name__ == "__main__":
    main()
