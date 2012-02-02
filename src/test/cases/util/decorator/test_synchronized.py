#!/usr/bin/env python
"""
Test cases for synchronized_class decorator in oan.util.decorator.synchronized

"""

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from threading import Thread
from threading import Lock
import time

from test.test_case import OANTestCase
from oan.util.decorator.synchronized import synchronized, NoLockObjectError

class ThreadSafeCrash(object):
    """Don't have the required lock object."""

    @synchronized
    def check_sync(self):
        pass


class ThreadSafe(object):
    """Will get a threading.Lock by @synchronized"""
    _id = None

    _lock = Lock()

    @synchronized
    def check_sync(self, id):
        self._id = id
        # If not synced, another thread will be able to update self._id
        time.sleep(0.01)

        if self._id != id:
            raise Exception("Not in sync (%s, %s)"  % (self._id, id))

# Shared by all threads
safe = ThreadSafe()


class MyThread(Thread):
    n = None
    def __init__(self, n):
        Thread.__init__(self)
        self.n = n

    def run(self):
        for i in range(5):
            safe.check_sync(i * self.n)


class TestSynchronized(OANTestCase):
    def test_NoLockObjectError(self):
        with self.assertRaises(NoLockObjectError):
            obj = ThreadSafeCrash()
            obj.check_sync()

    def test_sync(self):
        threads = [MyThread(i) for i in xrange(10)]

        for t in threads:
            t.start()

        for t in threads:
            t.join()
