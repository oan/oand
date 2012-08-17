#!/usr/bin/env python
'''
Test cases for util.log_counter

'''

__author__ = "martin@amivono.com, daniel@amivono.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin@amivono.com, daniel@amivono.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from test.test_case import OANTestCase

from oan.util import log_counter


class TestLogCounter(OANTestCase):
    def test_counter(self):
        log_counter.clear()
        self.assertEqual(log_counter.result(), "")

        log_counter.begin("test")
        log_counter.end("test")

        self.assertEqual(log_counter.result(), "\ntest                           -> counter:     1, total: 0.0000, avg: 0.0000, min: 0.0000, max: 0.0000")
        log_counter.clear()
