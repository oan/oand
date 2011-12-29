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

from oan_unittest import OANTestCase
import unittest
import time
import oan
from oan import node_manager

from oan_loop import OANLoop
from oan_event import OANEvent

from oan_node_manager import OANNode, OANNodeManager
from oan_message import OANMessagePing, OANMessageHeartbeat

from Queue import Queue

class TestOANServer(OANTestCase):
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
        if isinstance(message, OANMessagePing):
            if message.ping_counter == 0:
                self.queue.put(message)

    def create_watcher(self):
        node_manager().dispatcher.on_message += [self.got_message]

    def create_node(self):
        node = node_manager().create_node('n1', 'localhost', 8001)
        node_manager().set_my_node(node)

        node_manager().create_node('xx:hh:10', 'localhost', 4000)
        node_manager().create_node('xx:hh:11', 'localhost', 4001)
        node_manager().create_node('xx:hh:12', 'localhost', 4002)
        node_manager().create_node('xx:hh:13', 'localhost', 4003)

    def test_message_ping(self):
        for n in xrange(10, 14):
            for i in xrange(5):
                node_manager().send('xx:hh:%d' % n, OANMessagePing.create( "N%dP%d" % (n, i), 11 )) # the ping will be transfered 11 times

        counter = 0
        for i in xrange(20):
            message = self.queue.get()
            counter += 1
