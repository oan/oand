#!/usr/bin/env python
"""
Test cases for synchronized decorator in oan.util.decorator.capture

"""

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import sys

from test.test_case import OANTestCase
from oan.util.decorator.capture import capture


class Test():
    @capture
    def write(self):
        sys.stdout.write("This is stdout")
        sys.stderr.write("This is stderr")


class TestCapture(OANTestCase):
    def test_capture(self):
        test = Test()
        stdout, stderr = test.write()
        self.assertEqual(stdout, "This is stdout")
        self.assertEqual(stderr, "This is stderr")
