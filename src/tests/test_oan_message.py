#!/usr/bin/env python
'''
Test cases for oan_message.py

'''

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from oan_unittest import OANTestCase
import unittest
import time
import oan
from oan import node_manager

from oan_loop import OANLoop
from oan_event import OANEvent

from oand import OANApplication
from oan_config import OANConfig
from oan_node_manager import OANNetworkNode, OANNodeManager
from oan_message import OANMessagePing, OANMessageHeartbeat, OANMessageClose, OANMessageHandshake

from Queue import Queue

class TestOANMessage(OANTestCase):
    queue = None
    app = None

    def setUp(self):
        self.queue = Queue()

        self.app = OANApplication(OANConfig(
            "tt:tt:10",
            "TestOANMessage",
            "localhost",
            str(8000)
        ))

        self.app.run()
        self.create_node()
        node_manager().server.on_bridge_added.append(self.bridge_added)
        node_manager().server.on_bridge_removed.append(self.bridge_removed)

    def tearDown(self):
        node_manager().server.on_bridge_added.remove(self.bridge_added)
        node_manager().server.on_bridge_removed.remove(self.bridge_removed)
        self.queue = None
        self.app.stop()

    def bridge_added(self, bridge):
        print "got_connection"
        self.queue.put("got_connection")

    def bridge_removed(self, bridge):
        print "got_close"
        self.queue.put("got_close")

    def create_node(self):
        node_manager().create_node('xx:hh:10', 'localhost', 4000)

    # test close message wait for idle.
    def test_message_close(self):
        for i in xrange(2):
            # open a connection to server.
            node_manager().send('xx:hh:10', OANMessageHeartbeat.create(node_manager().get_my_node()))

            # Wait for close mesage
            called = self.queue.get(True, 10)
            self.assertEqual(called, "got_connection")

            called = self.queue.get(True, 10)
            self.assertEqual(called, "got_close")
