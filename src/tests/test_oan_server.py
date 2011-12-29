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


# test and see what happends if n1 connects to n2 at same time as n2 connect to n1.
class TestOAN(OANTestCase):
    queue = None
    app = None

    def setUp(self):
        self.queue = Queue()

        self.app = OANApplication(OANConfig(
            "tt:tt:10",
            "TestOAN",
            "localhost",
            str(8000)
        ))

        self.app.run()
        self.create_node()
        self.create_watcher()

    def tearDown(self):
        self.app.stop()
        self.queue = None

    def got_message(self, message):
        if isinstance(message, OANMessagePing):
            if message.ping_counter == 1:
                self.queue.put(message)

    def create_watcher(self):
        node_manager().dispatcher.on_message += [self.got_message]

    def create_node(self):
        node_manager().create_node('xx:hh:10', 'localhost', 4000)
        node_manager().create_node('xx:hh:11', 'localhost', 4001)
        node_manager().create_node('xx:hh:12', 'localhost', 4002)
        node_manager().create_node('xx:hh:13', 'localhost', 4003)


    def test_message_nodelist(self):
        node_manager().send('xx:hh:10', OANMessageNodeSync.create())
        message = self.queue.get() # wait forever

    def test_message_ping(self):
        for n in xrange(10, 14):
            for i in xrange(5):
                node_manager().send('xx:hh:%d' % n, OANMessagePing.create( "N%dP%d" % (n, i), 10 ))
                # the ping will be transfered 10 times

        counter = 0
        for i in xrange(20):
            message = self.queue.get()
            counter += 1

        self.assertEqual(counter, 20)  # 4 * 5

