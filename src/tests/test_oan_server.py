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

#from oan_unittest import OANTestCase
import unittest
import time
import oan
from oan import node_manager

from oan_loop import OANLoop
from oan_event import OANEvent

from oan_node_manager import OANNode, OANNodeManager
from oan_message import OANMessagePing

from Queue import Queue

class TestOANServer(unittest.TestCase):
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
        self.loop.on_shutdown += (node_manager().shutdown, )
        self.loop.start()

    def stop_loop(self):
        self.loop.stop()
        self.loop.join()
        self.loop = None

    def got_message(self, message):
        print "got message"
        self.queue.put(message)

    def create_watcher(self):
        node_manager().dispatcher.on_message_after += [self.got_message]

    def create_node(self):
        node = OANNode('n1', 'localhost', 8001)
        node_manager().set_my_node(node)
        node_manager().add_node(node)

    def test_connect(self):
        node_manager().send('n1', OANMessagePing.create('n1'))
        message = self.queue.get() # max 10 sec wait
        self.assertEqual(message.uuid, 'n1')

    def test_message_ping(self):
        node_manager().send('n1', OANMessagePing.create('n1'))
        message = self.queue.get() # max 10 sec wait
        self.assertEqual(message.uuid, 'n1')
