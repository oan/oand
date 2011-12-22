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
from oan import node_manager

from oan_node_manager import OANNode, OANNodeManager
from oan_server import OANServer
from oan_loop import OANLoop
from oan_message import OANMessagePing


def my_bridge_added(bridge):
    print "my_bridge_added connected to %s" % (bridge.node.uuid)

def my_bridge_removed(bridge):
    print "my_bridge_removed"

def my_bridge_idle(bridge):
    print "my_bridge_idle"
    #bridge.shutdown()

def got_message(message):
    print "got message"
    node_manager().send('n1', message)
    #self.queue.put(message)

def create_watcher():
    node_manager().dispatcher.on_message += [got_message]

def main():

    n2_node = OANNode('n2', 'localhost', 8002)
    manager = OANNodeManager()
    oan.set_managers("None", "None", manager)
    manager.set_my_node(n2_node)
    node_manager().dispatcher.start()
    create_watcher()

    loop = OANLoop()
    loop.start()

    try:
        while True:
            time.sleep(10)

    except KeyboardInterrupt:
        pass

    finally:
        loop.stop()

if __name__ == "__main__":
    main()
