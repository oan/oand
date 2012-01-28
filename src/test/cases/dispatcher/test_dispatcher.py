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
from threading import Thread, Lock
from Queue import Queue

from oan.util import log
from oan.dispatcher import OANMessageDispatcher
from test.test_case import OANTestCase


class OANTestMessageSelect:
    """
    A test message to yield many values from a message.
    """
    def execute(self):
        for i in xrange(10):
            yield "My select [%d]" % i


class OANTestMessageReturn:
    """
    A simple test message to return one value.
    """
    def execute(self):
        yield "My return value"


class OANTestMessageStatic:
    """
    A static test message that will be put in the dispatcher
    without a instance.
    """

    @staticmethod
    def execute():
        yield "My return from static message"


class TestOANMessageDispatcher(OANTestCase):

    _dispatcher = None

    def setUp(self):
        self._dispatcher = OANMessageDispatcher(None)

    def tearDown(self):
        self._dispatcher.shutdown()
        self._dispatcher = None

    def test_select(self):
        i = 0
        for s in self._dispatcher.select(OANTestMessageSelect()):
            self.assertEqual(s, "My select [%d]" % i)
            i += 1

    def test_get(self):
        value = self._dispatcher.get(OANTestMessageReturn())
        self.assertEqual(value, "My return value")

    def test_static(self):
        value = self._dispatcher.get(OANTestMessageStatic)
        self.assertEqual(value, "My return from static message")

