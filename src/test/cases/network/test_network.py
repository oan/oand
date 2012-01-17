#!/usr/bin/env python
'''
Test cases for oan.network.py

'''

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from test.test_case import OANTestCase

from datetime import datetime, timedelta

import unittest
import socket
import timeit
import time
import oan
import uuid
import threading
from threading import Thread, Lock
from network.oan_network import OANNetwork, OANTimer, OANNetworkMessageListen, OANNetworkMessageConnectOan

from Queue import Queue

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


class OANNetworkMessageException:
    exception = None

    @classmethod
    def create(cls, exception):
        obj = cls()
        obj.exception = exception
        return obj

    def execute(self, server):
        raise self.exception


_counter = None
def counter():
    return _counter

_network = None
def network():
    return _network

class TestOANNetwork(OANTestCase):

    def setUp(self):
        global _counter, _network

        _counter = OANTestCounter()
        _network = OANNetwork(None)

    def tearDown(self):
        global _counter, _network

        network().shutdown()
        _network = None
        _counter = None

    '''
    test_listen
    '''
    def test_listen(self):
        port = 8010

        host = network().get(OANNetworkMessageListen.create(port))
        connected = False
        for i in xrange(1,10):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            err = s.connect_ex((host, 8010))
            if err == 0:
                connected = True
                break

            time.sleep(1)

        self.assertTrue(connected)



    '''
    test_connect_oan
    '''
    message_bff_connect = None
    timer_connect = None

    def my_bridge_added(self, bridge):
        print "got in my_bridge_added"
        if bridge.node.host == message_bff_connect.host and bridge.node.port == message_bff_connect.port:
            print "connected in my_bridge_added"
            network().remove_timer(self.timer_connect)

    def my_timer_connect(self):
        network().execute(self.message_bff_connect)

    def test_connect_oan(self):
        self.timer_connect = OANTimer(2, self.my_timer_connect)
        self.message_bff_connect = OANNetworkMessageConnectOan.create('localhost', 4000)

        network().on_bridge_added(self.my_bridge_added)
        network().add_timer(self.timer_connect)

        while True:
            time.sleep(10)


    '''
    test_error
    '''
    got_error_queue = None

    def got_error(self, message, ex):
        self.got_error_queue.put(ex)

    def test_error(self):
        self.got_error_queue = Queue()

        #Test exception with execute method and on_error event
        ex = Exception("my test exception")
        network().on_error.append(self.got_error)
        network().execute(OANNetworkMessageException.create(ex))
        self.assertEqual(self.got_error_queue.get(), ex)

        #Test exception with get method
        #maybe write our own assertException and assertNotException in oanunittest
        #self.assertRaises(ex, network().get, OANNetworkMessageException.create(ex))
        try:
            network().get(OANNetworkMessageException.create(ex))
            self.assertFalse(True)
        except Exception, e:
            self.assertTrue(True)

    """

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

        self.assertEqual(got_message_queue.get(), m)
        dispatcher().on_message.remove(self.got_message)


    '''

    '''
    def test_threads(self):
        # generate a lot of inc and dec message that will be executed, sum should be zero
        network().generate()
        # stop the dispatcher and wait for threads to finish
        dispatcher().stop()
        self.assertEqual(counter().get_value(), 0)

    """
