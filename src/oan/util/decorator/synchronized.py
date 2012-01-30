#!/usr/bin/env python
"""
Synchronize two (or more) functions on an instance.

Read more
    http://wiki.python.org/moin/PythonDecoratorLibrary#Synchronization
"""

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.2"
__status__ = "Test"

from threading import Lock


def synchronized(obj):
    """
    Synchronize two (or more) functions on an instance.

    The decorator will create a Lock() on the owning instance of the decorated
    function. Only one synchronized function can then be processed at a time.
    Other threads calling the same function will have to wait until the first
    thread are done.

    Example:
    class ThreadSafe(object):
        @synchronized_class
        def check_sync(self, id):
            pass

    """

    def wrap(self, *args, **kw):
        if hasattr(self, "_lock"):
            lock = getattr(self, "_lock")
        else:
            lock = Lock()
            setattr(self, "_lock", lock)

        lock.acquire()
        try:
            return obj(self, *args, **kw)
        finally:
            lock.release()
    return wrap
