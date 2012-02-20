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
from signal import SIGTERM, SIGINT, SIG_IGN

class MyTestInterrupt(Exception): pass

class TestSignalHandler(OANTestCase):

    def setUp(self):
        OANSignalHandler.register(SIGINT, MyTestInterrupt)

    def tearDown(self):
        OANSignalHandler.reset(SIGINT)

    def test_set(self):
        # A signal can be set more than once but only one interrupt should
        # be raised.
        OANSignalHandler.set(SIGINT)
        OANSignalHandler.set(SIGINT)
        with self.assertRaises(MyTestInterrupt):
            OANSignalHandler.wait()

        # the signal should not raise a interrupt before it has been reset
        OANSignalHandler.set(SIGINT)

    def test_reset(self):
        OANSignalHandler.set(SIGINT)
        with self.assertRaises(MyTestInterrupt):
            OANSignalHandler.wait()

        # reset the signal so it can be raised again
        OANSignalHandler.reset(SIGINT)
        OANSignalHandler.set(SIGINT)
        with self.assertRaises(MyTestInterrupt):
            OANSignalHandler.wait()

    def test_wait_timeout(self):
        OANSignalHandler._timeout = 1
        with self.assertRaises(MyTestInterrupt):
            OANSignalHandler.wait()



