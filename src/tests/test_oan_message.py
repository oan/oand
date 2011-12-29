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

from oan_node_manager import OANNode, OANNodeManager
from oan_message import OANMessagePing, OANMessageHeartbeat, OANMessageClose, OANMessageHandshake

from Queue import Queue

class TestOANMessage(OANTestCase):
    loop = None
    queue = None

    def setUp(self):
        self.queue = Queue()
        oan.set_managers("None", "None", OANNodeManager())
        self.start_loop()
        self.create_node()
        self.create_watcher()

    def tearDown(self):
        self.stop_loop()
        oan.set_managers("None", "None", "None")
        self.queue = None

    def start_loop(self):
        self.loop = OANLoop()
        self.loop.on_shutdown += [node_manager().shutdown]
        self.loop.start()

    def stop_loop(self):
        self.loop.stop()
        self.loop.join()
        self.loop = None

    def got_message(self, message):
        self.queue.put(message)

    def create_watcher(self):
        node_manager().dispatcher.on_message += [self.got_message]

    def create_node(self):
        node = node_manager().create_node('n1', 'localhost', 8001)
        node_manager().create_node('n2', 'localhost', 8002)
        node_manager().set_my_node(node)

    def test_message_close(self):
        # open a connection to server.
        node_manager().send('n1', OANMessageHeartbeat.create(node_manager().get_my_node()))

        # Wait for close mesage
        message = self.queue.get(True, 10)
        self.assertTrue(isinstance(message, OANMessageHandshake))
        message = self.queue.get(True, 10)
        self.assertTrue(isinstance(message, OANMessageHandshake))
        message = self.queue.get(True, 10)
        self.assertTrue(isinstance(message, OANMessageHeartbeat))
        message = self.queue.get(True, 10)
        self.assertTrue(isinstance(message, OANMessageClose))
