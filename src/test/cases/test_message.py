#!/usr/bin/env python
'''
Test cases for oan.message.py

'''

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from test.test_case import OANTestCase
import unittest
import time
import oan
import uuid
from oan import loop, node_manager

from oan.loop import OANLoop
from oan.event import OANEvent

from oan.application import OANApplication
from oan.config import OANConfig
from oan.node_manager import OANNetworkNode, OANNodeManager
from oan.message import OANMessagePing, OANMessageHeartbeat, OANMessageClose, OANMessageHandshake

from Queue import Queue

'''
class TestOANMessage(OANTestCase):
    queue = None
    app = None

    def setUp(self):
        self.queue = Queue()

        self.app = OANApplication(OANConfig(
            '00000000-0000-0000-8000-000000000000',
            'TestOANMessage',
            'localhost',
            str(8000)
        ))

        self.app.run()
        self.create_node()
        loop()._server.on_bridge_added.append(self.bridge_added)
        loop()._server.on_bridge_removed.append(self.bridge_removed)

    def tearDown(self):
        loop()._server.on_bridge_added.remove(self.bridge_added)
        loop()._server.on_bridge_removed.remove(self.bridge_removed)
        self.queue = None
        self.app.stop()

    def bridge_added(self, bridge):
        print "got_connection"
        self.queue.put("got_connection")

    def bridge_removed(self, bridge):
        print "got_close"
        self.queue.put("got_close")

    def create_node(self):
        node_manager().create_node(uuid.UUID('00000000-0000-0000-4004-000000000000'), 'localhost', 4004, False)

    # test close message wait for idle.
    def test_message_close(self):
        for i in xrange(1):
            # open a connection to server.
            node_manager().send(uuid.UUID('00000000-0000-0000-4004-000000000000'),
                                OANMessageHeartbeat.create(node_manager().get_my_node()))

            # Wait for connection
            called = self.queue.get(True, 10)
            self.assertEqual(called, "got_connection")

            # Wait for close mesage
            called = self.queue.get(True, 10)
            self.assertEqual(called, "got_close")

    '''
