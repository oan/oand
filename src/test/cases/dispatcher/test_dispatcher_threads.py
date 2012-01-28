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


"""
A global counter object to test thread lock. all threads and messages
will call this object.
"""
_counter = None
def counter():
    return _counter

class OANTestCounter:
    """
    Simulates a manager or statistic object that should be access throw dispatcher,
    this objects must be thread safe. USE Lock.

    """
    _value = 0
    _lock = Lock()

    def inc_counter(self, v):
        with self._lock:
            t = self._value
            #time.sleep(0.01)
            self._value = t + v
            #log.info("Inc: %s" % self._value)

    def dec_counter(self, v):
        with self._lock:
            t = self._value
            #time.sleep(0.01)
            self._value = t - v
            #log.info("Dec: %s" % self._value)

    def dump(self):
        with self._lock:
            log.info("Counter: %s" % self._value)

    # Return primitive, tuple or other thread safe data.
    # Note: lists, mutable data etc. are not thread safe.
    def get_value(self):
        with self._lock:
            return self._value



class OANTestMessageInc:
    """
    A test message to increse counter object
    """
    _value = None

    def __init__(self, value):
        self._value=value

    def execute(self):
        counter().inc_counter(self._value)



class OANTestMessageDec:
    """
    A test message to decrese counter object
    """
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
            if i % 100 == 0:
                log.info("Generated %d %s on %s:" % (i, self._cls.__name__, self.name))

            self._dispatcher.execute(self._cls(1))

        log.info("Generated done %s on %s:" % (self._cls.__name__, self.name))


class TestOANMessageDispatcherThreads(OANTestCase):

    _dispatcher = None

    def setUp(self):
        global _counter
        _counter = OANTestCounter()
        self._dispatcher = OANMessageDispatcher(None)


    def tearDown(self):
        global _counter
        _counter = None
        self._dispatcher.shutdown()
        self._dispatcher = None


    def test_threads(self):
        threads = []

        # Generate 60000 inc and dec messages that will be executed, sum
        # should be zero
        threads.append(OANTestMessageGenerator(self._dispatcher, OANTestMessageInc, 10000))
        threads.append(OANTestMessageGenerator(self._dispatcher, OANTestMessageInc, 10000))
        threads.append(OANTestMessageGenerator(self._dispatcher, OANTestMessageInc, 10000))
        threads.append(OANTestMessageGenerator(self._dispatcher, OANTestMessageDec, 30000))

        # Wait for all generator threads to finish. Dispatcher is already
        # started so it will start processing the messages during generation.
        for g in threads:
            g.join()

        # Stop the dispatcher and wait for threads to finish
        self._dispatcher.shutdown()

        # The sum of all OANTestMessageInc and OANTestMessageDec should be zero.
        # If you remove the Lock in counter object there will be a raise condition
        # and the sum will not be zero.
        self.assertEqual(counter().get_value(), 0)


