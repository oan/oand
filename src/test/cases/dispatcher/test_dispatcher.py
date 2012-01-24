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
import oan_id
from threading import Thread, Lock
from Queue import Queue

from oan.util import log
from oan.dispatcher import OANMessageDispatcher
from test.test_case import OANTestCase

_counter = None
def counter():
    return _counter

_dispatcher = None
def dispatch():
    return _dispatcher

class TestOANMessageDispatcher(OANTestCase):

    def setUp(self):
        global _dispatcher, _counter

        _dispatcher = OANMessageDispatcher(None)
        _counter = OANTestCounter()

    def tearDown(self):
        global _dispatcher, _counter

        dispatch().shutdown()
        _counter = None
        _dispatcher = None

    #

    def test_execute(self):
        dispatch().execute(OANTestMessageInc(1))
        self.assertTrueWait(lambda : counter().get_value() == 1)

    #

    class OANTestMessageSelect:
        def execute(self):
            for i in xrange(10):
                yield "My select [%d]" % i

    def test_select(self):
        i = 0
        for s in dispatch().select(self.OANTestMessageSelect()):
            self.assertEqual(s, "My select [%d]" % i)
            i += 1

    #

    class OANTestMessageReturn:
        def execute(self):
            yield "My return value"

    def test_get(self):
        value = dispatch().get(self.OANTestMessageReturn())
        self.assertEqual(value, "My return value")

    #

    class OANMessageStatic:
        @staticmethod
        def execute():
            pass

    got_message_queue = None

    def got_message(self, message):
        self.got_message_queue.put(message)

    def test_events(self):
        self.got_message_queue = Queue()

        dispatch().on_message.append(self.got_message)
        dispatch().execute(self.OANMessageStatic)

        self.assertEqual(self.got_message_queue.get(), self.OANMessageStatic)
        dispatch().on_message.remove(self.got_message)

    #

    class OANTestMessageGenerator(Thread):
        cls = None
        number = None

        def __init__(self, cls, number):
            Thread.__init__(self)
            self.cls = cls
            self.number = number
            Thread.start(self)

        def run(self):
            for i in xrange(self.number):
                #print "Generated %s on %s:" % (self.cls.__name__, self.name)
                dispatch().execute(self.cls(1))

            log.info("Generated done %s on %s:" % (self.cls.__name__, self.name))

    def test_threads(self):
        threads = []

        # Generate a lot of inc and dec messages that will be executed, sum
        # should be zero
        threads.append(self.OANTestMessageGenerator(OANTestMessageInc, 10000))
        threads.append(self.OANTestMessageGenerator(OANTestMessageInc, 10000))
        threads.append(self.OANTestMessageGenerator(OANTestMessageInc, 10000))
        threads.append(self.OANTestMessageGenerator(OANTestMessageDec, 30000))

        for g in threads:
            g.join()

        # Stop the dispatcher and wait for threads to finish
        dispatch().shutdown()

        self.assertEqual(counter().get_value(), 0)

    #

    got_error_queue = None

    class OANTestMessageException:
        exception = None

        @classmethod
        def create(cls, exception):
            obj = cls()
            obj.exception = exception
            return obj

        def execute(self):
            raise self.exception

    def got_error(self, message, ex):
        self.got_error_queue.put(ex)

    def test_error(self):
        self.got_error_queue = Queue()

        #Test exception with execute method and on_error event
        ex = Exception("my test exception")
        dispatch().on_error.append(self.got_error)
        dispatch().execute(self.OANTestMessageException.create(ex))
        self.assertEqual(self.got_error_queue.get(), ex)

        #Test exception with get method
        with self.assertRaises(Exception):
            dispatch().get(self.OANTestMessageException.create(ex))

class OANTestCounter:
    """
    Simulates a manager or statistic object that should be locked.

    """
    _value = 0
    _lock = Lock()

    def inc_counter(self, v):
        with self._lock:
            t = self._value
            #time.sleep(0.01)
            self._value = t + v
            #print "Inc: %s" % self._value

    def dec_counter(self, v):
        with self._lock:
            t = self._value
            #time.sleep(0.01)
            self._value = t - v
            #print "Dec: %s" % self._value

    def dump(self):
        with self._lock:
            log.info("Counter: %s" % self._value)

    # Return primitive, tuple or other thread safe data.
    # Note: lists, mutable data etc. are not thread safe.
    def get_value(self):
        with self._lock:
            return self._value

class OANTestMessageInc:
    _value = None

    def __init__(self, value):
        self._value=value

    def execute(self):
        counter().inc_counter(self._value)

class OANTestMessageDec:
    _value = None

    def __init__(self, value):
        self._value=value

    def execute(self):
        counter().dec_counter(self._value)
