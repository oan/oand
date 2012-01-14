#!/usr/bin/env python
'''

'''

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import time
import oan
import uuid

from datetime import datetime, timedelta
from threading import Thread, Lock
from Queue import Queue


class OANMessageShutdown:
    def execute(self):
        pass

class OANMessageWorker(Thread):

    _pass = None
    def __init__(self, passthru):
        Thread.__init__(self)
        self._pass = passthru

    def start(self):
        Thread.start(self)

    def run(self):
        q = self._pass

        print "Start worker %s" % self.name
        while True:
            (message, back) = q.get()
            try:
                ret = message.execute()
                self._pass.result(ret, back)
            except Exception as ex:
                self._pass.error(ex, back)

            if isinstance(message, OANMessageShutdown):
                q.execute(message) #put back shutdown message for other worker threads
                break

        print "Stop worker %s" % self.name

class OANPassthru(Queue):

    def execute(self, message):
        self.put((message, None))

    def select(self, message):
        back = Queue()
        self.put((message, back))
        while True:
            ret=back.get()

            if isinstance(ret, Exception):
                raise ret

            if ret == None:
                break

            yield ret

    def error(self, ex, back):
        print ex
        if (back):
            back.put(ex)
            back.put(None)

    def result(self, ret, back):
        if (back):
            for rec in ret:
                back.put(rec)

            back.put(None)


class OANMessageDispatcher:

    config = None
    node_manager = None
    meta_manager = None
    data_manager = None

    _workers = []
    _pass = None

    def __init__(self, config):
        self._pass = OANPassthru()

    def execute(self, message):
        self._pass.execute(message)

    def select(self, message):
       return self._pass.select(message)

    def get(self, message):
        for ret in self._pass.select(message):
            return ret

    def stop(self):
        self._pass.execute(OANMessageShutdown())
        for worker in self._workers:
            worker.join()

    def start(self):
        for i in xrange(5):
            worker = OANMessageWorker(self._pass)
            worker.start()
            self._workers.append(worker)
