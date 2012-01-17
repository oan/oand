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
import uuid
from threading import Thread, Lock
from Queue import Queue

from oan.dispatcher import OANMessageDispatcher
from test.test_case import OANTestCase

class TestOANDispatcher(OANTestCase):

    def setUp(self):
        global _dispatcher, _counter, _generator

        _dispatcher = OANMessageDispatcher(None)
        _counter = OANTestCounter()
        _generator = OANTestGenerator()

    def tearDown(self):
        global _dispatcher, _counter, _network

        dispatcher().shutdown()
        _network = None
        _counter = None
        _dispatcher = None

    def test_execute(self):
        dispatcher().execute(OANTestMessageInc(1))
        # you don't know when excute is finish give it some time.
        time.sleep(0.1)
        self.assertEqual(counter().get_value(), 1)

    def test_select(self):
        i = 0
        for s in dispatcher().select(OANTestMessageSelect()):
            self.assertEqual(s, "My select [%d]" % i)
            i += 1

    def test_get(self):
        value = dispatcher().get(OANTestMessageReturn())
        self.assertEqual(value, "My return value")



    '''

    '''
    got_message_queue = None

    def got_message(self, message):
        self.got_message_queue.put(message)

    def test_events(self):
        self.got_message_queue = Queue()

        m = OANTestStatic
        dispatcher().on_message.append(self.got_message)
        dispatcher().execute(m)

        self.assertEqual(self.got_message_queue.get(), m)
        dispatcher().on_message.remove(self.got_message)


    '''

    '''
    def test_threads(self):
        # generate a lot of inc and dec message that will be executed, sum should be zero
        generator().generate()
        # stop the dispatcher and wait for threads to finish
        dispatcher().shutdown()
        self.assertEqual(counter().get_value(), 0)

# this would be a manager or statistic object, should be locked
class OANTestCounter:
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
            print "Counter: %s" % self._value

    #return primitive or tuple, NOT lists or other mutable data, or object that is return is thread safe.
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


class OANTestMessageSelect:
    def execute(self):
        for i in xrange(10):
            yield "My select [%d]" % i

class OANTestMessageReturn:
    def execute(self):
        yield "My return value"

class OANTestMessageException:
    def execute(self):
        raise Exception('My exception')

class OANTestStatic:
    @staticmethod
    def execute():
        return "My static return"


class OANTestMessageGenerator(Thread):
    cls = None
    number = None

    def __init__(self, cls, number):
        Thread.__init__(self)
        self.cls = cls
        self.number = number

    def start(self):
        Thread.start(self)

    def run(self):
        for i in xrange(self.number):
            #print "Generated %s on %s:" % (self.cls.__name__, self.name)
            dispatcher().execute(self.cls(1))

        print "Generated done %s on %s:" % (self.cls.__name__, self.name)


class OANTestGenerator:

    generators = []

    def generate(self):
        generator = OANTestMessageGenerator(OANTestMessageInc, 10000)
        generator.start()
        self.generators.append(generator)

        generator = OANTestMessageGenerator(OANTestMessageInc, 10000)
        generator.start()
        self.generators.append(generator)

        generator = OANTestMessageGenerator(OANTestMessageInc, 10000)
        generator.start()
        self.generators.append(generator)

        generator = OANTestMessageGenerator(OANTestMessageDec, 30000)
        generator.start()
        self.generators.append(generator)

        for g in self.generators:
            g.join()

_counter = None
def counter():
    return _counter

_dispatcher = None
def dispatcher():
    return _dispatcher

_generator = None
def generator():
    return _generator



