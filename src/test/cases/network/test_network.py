#!/usr/bin/env python
'''
Test communication (network, bridges, server etc.) between nodes.

'''

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from uuid import UUID
from Queue import Queue

from test.test_case import OANTestCase

from oan.manager import dispatcher, node_manager
from oan.dispatcher.message import OANMessagePing
from oan.dispatcher.command import OANCommandSendToNode
from oan.application import OANApplication
from oan.config import OANConfig

from oan.util.network import get_local_host


class TestOANNetwork(OANTestCase):
    """

    TODO: Test and see what happends if n1 connects to n2 at same time as n2
    connect to n1.

    """
    queue = None
    app = None

    def setUp(self):
        self.queue = Queue()

        self.app = OANApplication(OANConfig(
            '00000000-0000-0000-8000-000000000000',
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

    def create_node(self):
        """Create known nodes (instead of loading from db"""
        node_manager().create_node(UUID('00000000-0000-0000-4000-000000000000'), get_local_host(), 4000, False)
        node_manager().create_node(UUID('00000000-0000-0000-4001-000000000000'), get_local_host(), 4001, False)
        node_manager().create_node(UUID('00000000-0000-0000-4002-000000000000'), get_local_host(), 4002, False)
        node_manager().create_node(UUID('00000000-0000-0000-4003-000000000000'), get_local_host(), 4003, False)

    def got_message(self, message):
        if isinstance(message, OANMessagePing):
            if message.ping_counter == 1:
                self.queue.put(message)

    def create_watcher(self):
        dispatcher().on_message.append(self.got_message)

    # def test_message_ping(self):
    #     self.assertTrue(True)

    #     # Send a ping between all nodes 5x10 times.
    #     for n in xrange(4000, 4001):
    #         for i in xrange(5):
    #             dispatcher().execute(OANCommandSendToNode.create(
    #                 UUID('00000000-0000-0000-%s-000000000000' % n),
    #                 OANMessagePing.create( "N%dP%d" % (n, i), 10 )
    #             ))

    #     counter = 0
    #     for i in xrange(20):
    #         message = self.queue.get()
    #         counter += 1
    #         print counter

    #     self.assertEqual(counter, 20)  # 4 * 5

