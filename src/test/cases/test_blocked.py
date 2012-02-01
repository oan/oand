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

import time
import oan_id
from Queue import Queue

from test.test_case import OANTestCase
from oan.manager import dispatcher, node_manager
from oan.loop import OANLoop
from oan.event import OANEvent
from oan.node_manager import OANNodeManager
from oan.message import OANMessagePing, OANMessageHeartbeat, OANMessageNodeSync
from oan.application import OANApplication
from oan.config import OANConfig
from oan.util import log

class TestOANBlocked(OANTestCase):
    queue = None
    app = None

    def setUp(self):
        self.queue = Queue()

        # create a blocked node
        self.app = OANApplication(OANConfig(
            '00000000-0000-bbbb-8001-000000000000',
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
        if isinstance(message, OANMessagePing):
            self.queue.put(message)

    def create_watcher(self):
        dispatcher().on_message += [self.got_message]

    def create_node(self):
        pass
        #node_manager().create_node('oo:hh:18', 'localhost', 4008)

    def test_message_relay(self):
        # send a ping to a blocked node

        while not node_manager().exist_node(oan_id.UUID('00000000-0000-bbbb-4008-000000000000')):
            time.sleep(10)

        log.info("send ping")
        node_manager().send(oan_id.UUID('00000000-0000-bbbb-4008-000000000000'),
                                      OANMessagePing.create( "my relay ping", 2))
                                           # send ping back and forward (2)

        message = self.queue.get()
        log.info(message)
        # self.assertEqual(counter, 20)  # 4 * 5

