#!/usr/bin/env python
"""
Test cases for util.signal_handler

"""

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import os
import sys
from time import sleep

from test.test_case import OANTestCase

from oan.util.signal_handler import OANSignalHandler
from signal import SIGINFO

class MyTestInterrupt(Exception): pass

class TestSignalHandler(OANTestCase):

    def setUp(self):
        OANSignalHandler.register(SIGINFO, MyTestInterrupt)

    def tearDown(self):
        OANSignalHandler.reset(SIGINFO)
        OANSignalHandler.deactivate()

    def fire_signal(self, signum):
        OANSignalHandler.fire(signum)

    def test_set(self):
        # A signal can be set more than once but only one interrupt should
        # be raised.
        OANSignalHandler.set(SIGINFO)
        OANSignalHandler.set(SIGINFO)
        with self.assertRaises(MyTestInterrupt):
            OANSignalHandler.wait()

        # the signal should not raise a interrupt before it has been reset
        OANSignalHandler.set(SIGINFO)

    def test_set_after_wait(self):
        self.call_later(0.5, self.fire_signal, signum = SIGINFO)
        with self.assertRaises(MyTestInterrupt):
            OANSignalHandler.wait()


    def test_set_spam(self):

        for x in xrange(1,10):
           self.call_later(0.5, self.fire_signal, signum = SIGINFO)

        with self.assertRaises(MyTestInterrupt):
            OANSignalHandler.wait()


    def test_loop(self):
        self.call_later(0.5, self.fire_signal, signum = SIGINFO)
        while True:
            try:
                try:
                    OANSignalHandler.activate()
                    for x in xrange(1,10):
                        sleep(10)
                finally:
                    OANSignalHandler.deactivate()

            except MyTestInterrupt:
                self.assertTrue(True)
                break


    def test_reset(self):
        OANSignalHandler.set(SIGINFO)
        with self.assertRaises(MyTestInterrupt):
            OANSignalHandler.wait()

        # reset the signal so it can be raised again
        OANSignalHandler.reset(SIGINFO)
        OANSignalHandler.set(SIGINFO)
        with self.assertRaises(MyTestInterrupt):
            OANSignalHandler.wait()
