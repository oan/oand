#!/usr/bin/env python
'''
Test cases for OANQueue.

'''

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"


from Queue import Queue
from threading import Thread

from oan.util.queue import OANQueue
from time import time, sleep
from oan.util import log
from test.test_case import OANTestCase

class TestOANQueue(OANTestCase):

    number_of_items = 100000
    data = ["MESSAGE"]

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def putter(self, q, nums):
        for x in xrange(0, nums):
            q.put(self.data)

    def getter(self, q, nums):
        for x in xrange(0, nums):
            item = q.get()

    def test_push_oan_queue(self):
        start = time()

        q = OANQueue()
        for x in xrange(0, self.number_of_items):
            q.put(self.data)

        for x in xrange(0, self.number_of_items):
            item = q.get()

        elapsed = (time() - start)
        log.info("test_push_oan_queue, sec - %s, %s" % ((elapsed), len(q)))

    def test_push_queue(self):
        start = time()

        q = Queue()
        for x in xrange(0, self.number_of_items):
            q.put(self.data)

        for x in xrange(0, self.number_of_items):
            item = q.get()

        elapsed = (time() - start)
        log.info("test_push_queue, sec - %s, %s" % (elapsed, q.qsize()))

    def test_thread_oan_queue(self):
        start = time()
        q = OANQueue()
        t1 = Thread(target=self.putter, kwargs={'q': q, 'nums': self.number_of_items})
        t1.start()

        t2 = Thread(target=self.getter, kwargs={'q': q, 'nums': self.number_of_items})
        t2.start()

        t2.join()

        elapsed = (time() - start)
        log.info("test_thread_oan_queue, sec - %s, %s" % ((elapsed), len(q)))


    def test_thread_queue(self):
        start = time()
        q = Queue()
        t1 = Thread(target=self.putter, kwargs={'q': q, 'nums': self.number_of_items})
        t1.start()

        t2 = Thread(target=self.getter, kwargs={'q': q, 'nums': self.number_of_items})
        t2.start()

        t2.join()

        elapsed = (time() - start)
        log.info("test_thread_queue, sec - %s, %s" % ((elapsed), q.qsize()))







