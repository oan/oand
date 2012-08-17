#!/usr/bin/env python
'''
OANThread

We don't need to use this anymore, we will use our own network classes
and remove asyncore. (we used this to shutdown asyncore nicely)
'''

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from threading import Event, Thread

class OANThread(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.shutdown_event = Event()

    def enable_shutdown(self):
        self.shutdown_event.set()

    def disable_shutdown(self):
        self.shutdown_event.clear()

    def join(self):
        self.shutdown_event.wait()
