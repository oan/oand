#!/usr/bin/env python
'''
Test cases for oan.statistic.py

'''

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import time

from uuid import UUID
from Queue import Queue

from oan.util import log
from oan.dispatcher import OANMessageDispatcher
from test.test_case import OANTestCase

class OANTestMessageStaticEvent:
    @staticmethod
    def execute():
        pass

class TestOANMessageDispatcherEvent(OANTestCase):

    _dispatcher = None
    _got_message_queue = None


    def setUp(self):
        self._dispatcher = OANMessageDispatcher(None)
        # subscribe on_message event
        self._dispatcher.on_message.append(self._got_message)
        self._got_message_queue = Queue()


    def tearDown(self):
        self._dispatcher.shutdown()
        # unsubscribe on_message event
        self._dispatcher.on_message.remove(self._got_message)


    def _got_message(self, message):
        """
        When a message is processed this function will be called.
        it puts the message in a test queue just to signal the
        assertEqual that waits on the queue.
        """
        self._got_message_queue.put(message)


    def test_events(self):
        # execute the message
        self._dispatcher.execute(OANTestMessageStaticEvent)

        # wait for message from "_got_message"
        self.assertEqual(self._got_message_queue.get(), OANTestMessageStaticEvent)
