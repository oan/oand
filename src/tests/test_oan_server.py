#!/usr/bin/env python
'''
Test cases for oan_server.py

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import unittest

from oan_server import OANServer
from oan_bridge import OANBridge
from oan_loop import OANLoop
from oan_event import OANEvent
from oan_simple_node_manager import OANNode, OANNodeManager

class TestOANServer(unittest.TestCase):
    manager1 = None
    loop1 = None
    server1 = None

    manager2 = None
    loop2 = None
    server2 = None

    def setUp(self):
        self.create_node1()
        self.create_node2()

    def tearDown(self):
        self.manager1.stop()
        self.loop1.stop()

        self.manager2.stop()
        self.loop2.stop()

    def create_node1(self):
        '''Simulate creation of node 1 that will commnunicate with node2.'''
        node1 = OANNode('n1', 'localhost', 8001)
        node2 = OANNode('n2', 'localhost', 8002)
        self.server1 = server1 = OANServer(node1)

        self.manager1 = manager1 = OANNodeManager(server1)
        manager1.add_node(node1)
        manager1.add_node(node2)

        manager1.send('n1', 'my super cool queue message before connection')
        manager1.start()

        self.loop1 = loop1 = OANLoop()
        loop1.on_shutdown += (server1.shutdown, )
        loop1.start()

    def create_node2(self):
        '''Simulate creation of node 2 that will commnunicate with node1.'''
        node1 = OANNode('n1', 'localhost', 8001)
        node2 = OANNode('n2', 'localhost', 8002)
        self.server2 = server2 = OANServer(node2)

        self.manager2 = manager2 = OANNodeManager(server2)
        manager2.add_node(node1)
        manager2.add_node(node2)

        manager2.send('n1', 'my super cool queue message before connection')
        manager2.start()

        self.loop2 = loop2 = OANLoop()
        loop2.on_shutdown += (server2.shutdown, )
        loop2.start()

    def _test_all(self):
        self.assertTrue('n2' in self.server1.bridges)
        #    self.manager1.send('n1', ("clock [%s] from [%s]" % (datetime.datetime.now(), server.node.node_id)))
        self.assertTrue(True)

