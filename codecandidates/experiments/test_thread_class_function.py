#!/usr/bin/env python
"""
Test cases for util.daemon_base

"""

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from threading import Thread


class thread_class_function(Thread):
    L=None

    def __init__(self):
        Thread.__init__(self)
        Thread.start(self)

    def run(self):
        self.L = []
        for i in range(500000):
            self.L.append(i)

    def get(self):
        return self.L


def regular_function():
    L = []
    for i in range(500000):
        L.append(i)


###


def test1():
    L = []
    for i in range(5):
        L.append(thread_class_function())

    for t in L:
        t.get()


def test2():
    L = []
    for i in range(5):
        L.append(regular_function())

    for t in L:
        t


if __name__ == '__main__':
    from timeit import Timer

    t = Timer("test1()", "from __main__ import thread_class_function, test1")
    print "%.2f usec/pass" % (1000000 * t.timeit(number=1)/100000)

    t = Timer("test2()", "from __main__ import regular_function, test2")
    print "%.2f usec/pass" % (1000000 * t.timeit(number=1)/100000)
