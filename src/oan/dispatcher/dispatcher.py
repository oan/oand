#!/usr/bin/env python
"""

"""

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import time
import uuid
from datetime import datetime, timedelta
from threading import Thread, Lock
from Queue import Queue

from oan.event import OANEvent
from oan.passthru import OANPassthru
from oan.message import OANMessageShutdown

class OANMessageWorker(Thread):

    _pass = None
    def __init__(self, passthru):
        Thread.__init__(self)
        self._pass = passthru
        Thread.start(self)

    def run(self):
        q = self._pass

        print "Start message worker %s" % self.name

        while True:
            (message, back) = q.get()
            try:
                ret = message.execute()
                self._pass.result(ret, back)
            except Exception as ex:
                self._pass.error(message, ex, back)

            if isinstance(message, OANMessageShutdown):
                q.execute(message) #put back shutdown message for other worker threads
                break

        print "Stop message worker %s" % self.name



class OANMessageDispatcher:

    ''' Public '''
    config = None
    node_manager = None
    meta_manager = None
    data_manager = None

    ''' Event '''
    on_message = None

    ''' Privat '''
    _workers = []
    _pass = None

    def __init__(self, config):
        self._pass = OANPassthru()
        self.on_message = self._pass.on_message
        self._start()

    def execute(self, message):
        self._pass.execute(message)

    def select(self, message):
       return self._pass.select(message)

    def get(self, message):
        for ret in self._pass.select(message):
            return ret

    def shutdown(self):
        self._pass.execute(OANMessageShutdown())
        for worker in self._workers:
            worker.join()

    def _start(self):
        for i in xrange(5):
            worker = OANMessageWorker(self._pass)
            self._workers.append(worker)
