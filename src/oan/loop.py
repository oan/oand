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
import threading
from datetime import datetime, timedelta
from Queue import Queue
from threading import Thread

from oan.util import log
from oan.event import OANEvent
from oan.network import OANServer

class OANTimer(object):
    checked = None
    expires = None
    callback = None
    interval = None

    def __init__(self, sec, callback, *args, **kwargs):
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
        self.interval = sec
        self.later(self.interval)


    def later(self, sec):
        self.expires = datetime.utcnow() + timedelta(seconds = sec)

    def check(self):
        self.checked = datetime.utcnow()
        if (self.expires < self.checked):
            self.callback(*self.args, **self.kwargs)
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

    _server = None

    _running = False

    _timers = None

    _calls = None

    # wait for the thread to start and stop
    _started = None

    def __init__(self):
        Thread.__init__(self)
        self.on_start = OANEvent()
        self.on_shutdown = OANEvent()
        self.on_stop = OANEvent()
        self._started = threading.Event()
        self._timers = []
        self._calls = Queue()

    def start(self):
        if (not self._running):
            self._running = True
            Thread.start(self)
            #wait for set in run
            self._started.wait()

    def stop(self):
        self._running = False
        #wait for clear in run
        self._started.wait()

    def add_timer(self, timer):
        self._timers.append(timer)

    def remove_timer(self, timer):
        self._timers.remove(timer)

    def add_call(self, callback, *args, **kwargs):
        self._calls.put((callback, args, kwargs))

    def listen(self, node):
        self.add_call(self._server.start_listen, node)

    def connect_to_node(self, node):
        self.add_call(self._server.connect_to_node, node)

    def connect_to_oan(self, host, port):
        self.add_call(self._server.connect_to_oan, host, port)

    def run(self):
        log.info("OANLoop: started")
        self._server = OANServer()
        self.on_start()
        self._started.set()
        while(self._running):
            asyncore.loop(0.1, False, None, 10)
            for timer in self._timers:
                timer.check()

            if not self._calls.empty():
                (callback, args, kwargs) = self._calls.get(True, 1)
                callback(*args, **kwargs)

        log.info("OANLoop: shutdown")
        self.on_shutdown()
        self._server.shutdown()
        asyncore.loop()
        self.on_stop()
        self._started.clear()
        log.info("OANLoop stopped")
