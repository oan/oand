#!/usr/bin/env python
'''
RPC server handling request from oan clients.

'''

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import asyncore
import socket
import time
import thread
from datetime import datetime, timedelta
from Queue import Queue
from threading import Thread
from oan_event import OANEvent



class OANTimer(object):
    checked = None
    expires = None
    callback = None
    interval = None

    def __init__(self, sec, callback, *args, **kwargs):
        self.callback = callback
        self.interval = sec
        self.later(self.interval)

    def later(self, sec):
        self.expires = datetime.utcnow() + timedelta(seconds = sec)

    def check(self):
        self.checked = datetime.utcnow()
        if (self.expires < self.checked):
            self.callback()
            self.later(self.interval)
            return True

        return False

class OANLoop(Thread):

    ''' use: loop.on_start += my_loop_start() '''
    on_start = None

    ''' use: loop.on_shutdown += my_loop_shutdown() '''
    on_shutdown = None

    ''' use: loop.on_stop += my_loop_stop() '''
    on_stop = None

    _running = False

    _timers = None

    def __init__(self):
        Thread.__init__(self)
        self.on_start = OANEvent()
        self.on_shutdown = OANEvent()
        self.on_stop = OANEvent()
        self._timers = []

    def start(self):
        if (not self._running):
            self._running = True
            Thread.start(self)

    def stop(self):
        self._running = False

    def add_timer(self, timer):
        self._timers.append(timer)

    def run(self):
        print "OANLoop: started"
        self.on_start()
        while(self._running):
            asyncore.loop(0.1, False, None, 10)
            for timer in self._timers:
                timer.check()

        print "OANLoop: shutdown"
        self.on_shutdown()
        asyncore.loop()
        self.on_stop()
        print "OANLoop stopped"
