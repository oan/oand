#!/usr/bin/env python
'''
Test cases for OAN, test communication between nodes

'''

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from random import random

from test.test_case import OANTestCase
from oan.util.throttle import OANThrottle

class TestOanThrottle(OANTestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_max_throttle(self):
        OANThrottle.reset()
        max_cpu = None

        for x in xrange(1,15):
            for i in range(1, 1000000):
                b = 8*234*i*234

            OANThrottle.throttle(0.1)

            # wait 5 times to slow down to max cpu limit
            c = OANThrottle.current()

            if x > 10:
                if max_cpu is None or c > max_cpu:
                    max_cpu = c

                #print "current %s, max %s" % (c, max_cpu)

        self.assertLess(max_cpu, 0.15)


    def test_none_throttle(self):
        OANThrottle.reset()
        for x in xrange(1,15):
            for i in range(1, 1000000):
                b = 8*234*i*234

            sleep = OANThrottle.calculate(1.0)
            if x > 10:
                self.assertEqual(sleep, 0)

    def test_random_throttle(self):
        OANThrottle.reset()
        max_cpu = None

        for x in xrange(1,15):

            for i in range(1, int(random() * 2) * 100000):
                b = 8*234*i*234

            OANThrottle.throttle(0.1)

            # wait 10 times to slow down to max cpu limit
            c = OANThrottle.current()

            if x > 10:
                if max_cpu is None or c > max_cpu:
                    max_cpu = c

                #print "current %s, max %s" % (c, max_cpu)

        self.assertLess(max_cpu, 0.15)
