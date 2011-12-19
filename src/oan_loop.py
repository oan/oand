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
from Queue import Queue
from threading import Thread
from oan_bridge import OANBridge
from oan_event import OANEvent

class OANLoop(Thread):

    ''' use: loop.on_start += my_loop_start() '''
    on_start = OANEvent()

    ''' use: loop.on_shutdown += my_loop_shutdown() '''
    on_shutdown = OANEvent()

    ''' use: loop.on_stop += my_loop_stop() '''
    on_stop = OANEvent()

    _running = False

    def __init__(self):
        Thread.__init__(self)

    def start(self):
        if (not self._running):
            self._running = True
            Thread.start(self)

    def stop(self):
        self._running = False

    def run(self):
        print "OANLoop: started"
        self.on_start()
        while(self._running):
            asyncore.loop(0.3, False, None, 2)
            #print "OANLoop: check if running"

        print "OANLoop: shutdown"
        self.on_shutdown()
        asyncore.loop()
        self.on_stop()
        print "OANLoop stopped"
