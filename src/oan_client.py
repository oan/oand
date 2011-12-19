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

import oan
from oan_simple_node_manager import OANNode, OANNodeManager
from oan_server import OANServer
from oan_loop import OANLoop
from oan_message import OANMessagePing


def my_bridge_added(bridge):
    print "my_bridge_added connected to %s" % (bridge.node.node_id)
 #   if (bridge.node.node_id == 'n1'):
  #      bridge.out_queue.put("Welcome message from [%s]" % bridge.server.node.node_id);

def my_bridge_removed(bridge):
    print "my_bridge_removed"

def my_bridge_idle(bridge):
    pass
    #print "my_bridge_idle"
    #bridge.shutdown()

def main():

    n1_node = OANNode('n1', 'localhost', 8001)
    n1_server = OANServer(n1_node)

    n2_node = OANNode('n2', 'localhost', 8002) #remote

    manager = OANNodeManager(n1_server)
    oan.set_managers("None", "None", manager)
    manager.add_node(n1_node)
    manager.add_node(n2_node)

    n1_server.on_bridge_added += (my_bridge_added, )
    n1_server.on_bridge_removed += (my_bridge_removed, )
    n1_server.on_bridge_idle += (my_bridge_idle, )

    loop = OANLoop()
    loop.on_shutdown += (n1_server.shutdown, )
    loop.start()

    try:
        while True:
            manager.send('n2', OANMessagePing.create('n2'))
            time.sleep(10)

    except KeyboardInterrupt:
        pass

    finally:
        loop.stop()

if __name__ == "__main__":
    main()
