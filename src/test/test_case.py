#!/usr/bin/env python
"""
A replacement and inheritence of unittest.TestCase

Add functionality to the existing TestCase class.

"""

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import sys
import unittest
from time import time, sleep
from threading import Timer

class OANMatcherClass(object):
    cls_ = None
    def __init__(self, cls):
        self._cls = cls

    def __eq__(self, other):
        return other.__class__ == self._cls


class OANTestCase(unittest.TestCase):

    # Todo: Fix it
    # def run(self, result=None):
    #     """
    #     This is almost the same code as in the base class. The difference is the
    #     handling of tearDown, that will be executed when a KeyboardInterrupt
    #     exception is raised.

    #     """
    #     try:
    #         unittest.TestCase.run(self, result)
    #     except KeyboardInterrupt:
    #         print "KeyboardInterrupt"


    def call_later(self, seconds, callback, *args, **kwargs):
        t = Timer(seconds, callback, args, kwargs)
        t.start()

    def wait(self, condition, timeout = 5):
        """
        Wait until the function given by condition returns True.

        condition
            Function that will be executed until it returns true.

        timeout
            Number of seconds to wait until timeout and return False.

        return
            True if condtion was met.

        """
        endtime = time() + timeout
        result = False
        while (endtime > time()):
            result = condition()
            if result:
                break
            sleep(0.1)

        return result

    def assertTrueWait(self, condition, timeout = 5):
        """
        Wait until the function given by condtion returns True.

        timeout
            Number of seconds to wait until timeout and return False.

        Example:
            self.assertTrueWait(lambda : 'n2' in node_list)

        """
        self.assertTrue(self.wait(condition, timeout))


    assert_counters = {}
    def reset_all_counters(self):
        self.assert_counters = {}

    def reset_counter(self, key):
        self.assert_counters[key] = 0

    def inc_counter(self, key, number = 1):
        if key not in self.assert_counters:
            self.assert_counters[key] = 0

        self.assert_counters[key] += number

    def dec_counter(self, key, number = 1):
        if key not in self.assert_counters:
            self.assert_counters[key] = 0

        self.assert_counters[key] -= number

    def assert_counter_wait(self, key, value):
        if key not in self.assert_counters:
            self.assert_counters[key] = 0

        self.assertTrueWait(lambda : self.assert_counters[key] == value)



