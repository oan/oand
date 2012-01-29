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

class OANTestMessageException:
    """
    A test message that will raise a exception.
    """
    exception = None

    @classmethod
    def create(cls, exception):
        obj = cls()
        obj.exception = exception
        return obj

    def execute(self):
        raise self.exception



class TestOANMessageDispatcherError(OANTestCase):

    _dispatcher = None
    _got_error_queue = None

    def setUp(self):
        self._dispatcher = OANMessageDispatcher(None)
        # subscribe on_message event
        self._dispatcher.on_error.append(self._got_error)
        self._got_error_queue = Queue()


    def tearDown(self):
        self._dispatcher.shutdown()
        # unsubscribe on_message event
        self._dispatcher.on_error.remove(self._got_error)


    def _got_error(self, message, ex):
        """
        When a message raises an exception this function will be called.
        it puts the exception in a test queue just to signal the
        assertEqual that waits on the queue.
        """
        self._got_error_queue.put(ex)

    def test_error(self):

        #Test exception with execute method and on_error event
        ex = Exception("my test exception")
        self._dispatcher.execute(OANTestMessageException.create(ex))

        #_got_error_queue.get() is blocking waiting for the on_error event.
        self.assertEqual(self._got_error_queue.get(), ex)

        #Test exception with get method it should raise the exception
        with self.assertRaises(Exception):
           self._dispatcher.get(self.OANTestMessageException.create(ex))
