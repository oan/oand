#!/usr/bin/env python
"""
Synchronize two (or more) functions on a given lock.

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

def synchronized_s(lock):
    """ Synchronization decorator. """

    def wrap(f, *args, **kw):
        lock.acquire()
        try:
            return f(*args, **kw)
        finally:
            lock.release()

    return wrap

def synchronized(obj):
    """ Synchronization decorator. """

    def wrap(self, *args, **kw):
        if hasattr(self, "_lock"):
            lock = getattr(self, "_lock")
            print "get lock"
        else:
            print "create lock"
            lock = Lock()
            setattr(self, "_lock", lock)
            print hasattr(self, "_lock")

        lock.acquire()
        try:
            return obj(self, *args, **kw)
        finally:
            lock.release()
    return wrap

def synchronizedss(obj):
    """ Synchronization decorator. """

    if hasattr(obj, '__class__'):
        print "class obj", obj
        class class_wrap(obj):
            print "self", obj
            if hasattr(obj, "_lock"):
                raise Exception("Already has lock")
            else:
                lock = Lock()

        return class_wrap
    elif hasattr(obj, '__call__'):
        print "func"
        def wrap(self, *args, **kw):
            print "self", self

            print "xxx"
            if hasattr(self, "_lock"):
                lock = getattr(self, "_lock")
                print "lock"
            else:
                print "no lock"
                raise Exception("Has no lock")

            lock.acquire()
            try:
                return obj(*args, **kw)
            finally:
                lock.release()
        print "ret wrap"
        return wrap


