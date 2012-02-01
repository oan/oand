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

from threading import Lock

from oan.util import log
from oan.dispatcher.dispatcher import OANDispatcher
from test.test_case import OANTestCase

_state = None
def state():
    """A global state object that will be changed by a message"""
    return _state


class OANTestState:
    """
    Simulates a manager or statistic object that should be accessed via
    dispatcher, this objects must be thread safe. USE Lock.

    """
    _value = 0
    _lock = Lock()

    def set_value(self, value):
        with self._lock:
            self._value = value
            log.info("Change state to: %s" % self._value)

    def get_value(self):
        with self._lock:
            return self._value

    def is_value(self, value):
        with self._lock:
            return self._value == value


class OANTestMessageExecute:
    """A test message that set the OANTestState value."""
    _value = None

    @classmethod
    def create(cls, value):
        obj = cls()
        obj._value = value
        return obj

    def execute(self):
        state().set_value(self._value)


class TestOANDispatcherExecute(OANTestCase):
    _dispatcher = None

    def setUp(self):
        global _state
        _state = OANTestState()

        self._dispatcher = OANDispatcher()

    def tearDown(self):
        global _state
        _state = None

        self._dispatcher.shutdown()
        self._dispatcher = None

    def test_execute(self):
        # create and execute message that would set the state value to 17
        self._dispatcher.execute(OANTestMessageExecute.create(17))

        # Wait for the state to be 17
        self.assertTrueWait(lambda : state().is_value(17))
