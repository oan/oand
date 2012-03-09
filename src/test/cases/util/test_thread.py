#!/usr/bin/env python
'''
Test cases for OAN, test deamon thread with shutdown option.

'''

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"


from time import sleep
from oan.util.thread import OANThread
from test.test_case import OANTestCase


class TestThread(OANThread):

    condition = False

    def __init__(self):
        OANThread.__init__(self)
        self.start()

    def run(self):
        while True:
            self.condition = True
            self.enable_shutdown()
            # unsafe code
            sleep(0.01)
            self.disable_shutdown()

            # safe code
            self.condition = False
            sleep(0.5)



class TestOANThread(OANTestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass


    def test_daemon_threads(self):
        ts = []
        for x in xrange(1,10):
            ts.append(TestThread())

        sleep(2)
        for t in ts:
            t.join()

        for t in ts:
            self.assertTrue(t.condition)




