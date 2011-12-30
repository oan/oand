#!/usr/bin/env python
'''
Test cases for OAN, test communication between nodes

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

from oan_node_manager import OANNodeManager
from oan_message import OANMessagePing, OANMessageHeartbeat, OANMessageNodeSync
from oand import OANApplication
from oan_config import OANConfig

from Queue import Queue

class TestOANBlocked(OANTestCase):
    queue = None
    app = None

    def setUp(self):
        self.queue = Queue()

        # create a blocked node
        self.app = OANApplication(OANConfig(
            "bb:tt:10",
            "TestOANBlocked",
            "localhost",
            str(8001),
            "Server-03",
            'localhost',
            str(4003),
            True
        ))

        self.app.run()
        self.create_node()
        self.create_watcher()

    def tearDown(self):
        self.app.stop()
        self.queue = None

    def got_message(self, message):
        pass
        #if isinstance(message, OANMessagePing):
        #    if message.ping_counter == 1:
        #        self.queue.put(message)

    def create_watcher(self):
        node_manager().dispatcher.on_message += [self.got_message]

    def create_node(self):
        pass
        #node_manager().create_node('oo:hh:18', 'localhost', 4008)

    def test_message_relay(self):
        # send a ping to a blocked node

        while True:
            time.sleep(10)
            if node_manager().exist_node('bb:hh:18'):
                node_manager().send('bb:hh:18', OANMessagePing.create( "my relay ping", 2)) # send ping back and forward (2)

        self.queue.get() # wait for ever

        self.assertEqual(counter, 20)  # 4 * 5

