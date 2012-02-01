#!/usr/bin/env python
'''
Test cases for util.decorator

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from threading import Thread, Lock
import time

from test.test_case import OANTestCase
from oan.util.decorator.synchronized import synchronized

class thread_safe(object):
    @synchronized
    def get_id(self):
        return self.id

    @synchronized
    def set_id(self, id):
        self._id = id

class MyThread(Thread):
    def __init__(self, n):
        Thread.__init__(self)
        self.n = n

    def run(self):
        """ Print out some stuff.

        The method sleeps for a second each iteration.  If another thread
        were running, it would execute then.
        But since the only active threads are all synchronized on the same
        lock, no other thread will run.
        """

        for i in range(5):
            #print 'Thread %d: Start %d...' % (self.n, i),
            time.sleep(0.1)
            #print '...stop [%d].' % self.n

class TestLogging(OANTestCase):
    def test_sync(self):
        self.assertTrue(True)

        threads = [MyThread(i) for i in range(10)]
        for t in threads:
            t.start()
        self.assertTrue(True)

        for t in threads:
            t.join()
        self.assertTrue(True)
