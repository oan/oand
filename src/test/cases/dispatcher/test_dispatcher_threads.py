#!/usr/bin/env python
"""
Test cases for oan.dispatcher.dispatcher

"""

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import time
from threading import Thread, Lock

from oan.dispatcher.dispatcher import OANDispatcher
from test.test_case import OANTestCase

_counter = None
def counter():
    """
    A global counter object to test thread lock. All threads and messages
    will call this object.

    """
    return _counter


class OANTestCounter:
    """
    Simulates a manager or statistic object that should be accessed through
    a dispatcher, this objects must be thread safe. USE Lock.

    """
    _value = 0
    _lock = Lock()

    def inc_counter(self, v):
        with self._lock:
            t = self._value
            time.sleep(0.01)
            self._value = t + v

    def dec_counter(self, v):
        with self._lock:
            t = self._value
            time.sleep(0.01)
            self._value = t - v

    # Return primitive, tuple or other thread safe data.
    # Note: lists, mutable data etc. are not thread safe.
    def get_value(self):
        with self._lock:
            return self._value


class OANTestMessageInc:
    """A test message to increse counter object."""
    _value = None

    def __init__(self, value):
        self._value=value

    def execute(self):
        counter().inc_counter(self._value)


class OANTestMessageDec:
    """A test message to decrese counter object"""
    _value = None

    def __init__(self, value):
        self._value=value

    def execute(self):
        counter().dec_counter(self._value)


class OANTestMessageGenerator(Thread):
    """
    A generator thread that queues up messages to the dispatcher
    the test starts several OANTestMessageGenerator

    """
    _cls = None
    _number = None
    _dispatcher = None

    def __init__(self, dispatcher, cls, number):
        Thread.__init__(self)
        self._dispatcher = dispatcher
        self._cls = cls
        self._number = number
        Thread.start(self)

    def run(self):
        for i in xrange(self._number):
            self._dispatcher.execute(self._cls(1))


class TestOANDispatcherThreads(OANTestCase):
    _dispatcher = None

    def setUp(self):
        global _counter
        _counter = OANTestCounter()
        self._dispatcher = OANDispatcher()

    def tearDown(self):
        global _counter
        _counter = None
        self._dispatcher.shutdown()
        self._dispatcher = None

    def test_threads(self):
        threads = []

        # Generate 60000 inc and dec messages that will be executed, sum
        # should be zero
        d = self._dispatcher
        threads.append(OANTestMessageGenerator(d, OANTestMessageInc, 100))
        threads.append(OANTestMessageGenerator(d, OANTestMessageInc, 100))
        threads.append(OANTestMessageGenerator(d, OANTestMessageInc, 100))
        threads.append(OANTestMessageGenerator(d, OANTestMessageDec, 300))

        # Wait for all generator threads to finish. Dispatcher is already
        # started so it will start processing the messages during generation.
        for g in threads:
            g.join()

        # Stop the dispatcher and wait for threads to finish
        d.shutdown()

        # The sum of all OANTestMessageInc and OANTestMessageDec should be
        # zero. If you remove the Lock in counter object there will be a raise
        # condition and the sum will not be zero.
        self.assertEqual(counter().get_value(), 0)
