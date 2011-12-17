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
from Queue import Queue

from oan_server import OANServer
from oan_loop import OANLoop

def my_bridge_added(bridge):
    print "my_bridge_added connected to %s" % (bridge.connected_to)
    if (bridge.connected_to == 's1'):
        bridge.out_queue.put("Welcome message from [%s]" % bridge.server.node_id);

def my_bridge_removed(bridge):
    print "my_bridge_removed"


def main():
    server = OANServer('c1', 'localhost', 8001)
    server.on_bridge_added += (my_bridge_added, )
    server.connect_to_node('localhost', 8002)

    loop = OANLoop()
    loop.on_shutdown += (server.shutdown, )
    loop.start()

    try:
        while True:
            time.sleep(5)
            if ('s1' in server.bridges):
                server.bridges['s1'].out_queue.put("clock [%s] from [%s]" % (datetime.datetime.now(), server.node_id))

    except KeyboardInterrupt:
        pass

    finally:
        loop.stop()

if __name__ == "__main__":
    main()
