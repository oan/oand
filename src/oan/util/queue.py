#!/usr/bin/env python
'''
A faster Queue class to be used instead of standard Queue.
If you don't need to wait on a get just use deque class it's threadsafe
and fast.

'''

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from collections import deque
from threading import Lock, Condition

class OANQueue:
    _lock = None
    _cond = None

    def __init__(self, list=None):
        self._lock = Lock()
        self._cond = Condition(self._lock)
        if not list:
            self.list = deque()
        else:
            self.list = deque(list)

    def __len__(self):
        return len(self.list)

    def interrupt(self):
        with self._lock:
            self._cond.notify()

    def put(self, data):
        with self._lock:
            self.list.append(data)
            if len(self.list) == 1:
                self._cond.notify()

    def get(self, block = True):
        with self._lock:
            if block and len(self.list) == 0:
                self._cond.wait()

            return self.list.popleft()
