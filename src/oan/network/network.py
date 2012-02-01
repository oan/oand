#!/usr/bin/env python
'''
Network thread that handles all the network traffic

'''

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import asyncore
from datetime import datetime, timedelta
from threading import Thread

from oan.util import log
from server import OANServer
from oan.passthru import OANPassthru
from oan.network.command import OANNetworkComandShutdown


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


class OANNetworkWorker(Thread):

    # === Private === #
    _timers = None
    _pass = None
    _server = None

    def __init__(self, passthru):
        Thread.__init__(self)

        self._server = OANServer()
        self._pass = passthru
        self._timers = []
        Thread.start(self)

    def add_timer(self, timer):
        self._timers.append(timer)

    def remove_timer(self, timer):
        self._timers.remove(timer)

    def run(self):
        q = self._pass
        log.info("Start network worker %s" % self.name)

        while True:
            asyncore.loop(0.1, False, None, 10)

            for timer in self._timers:
                timer.check()

            if not q.empty():
                (message, back) = q.get()
                try:
                    ret = message.execute(self._server)
                    self._pass.result(ret, back)
                except Exception as ex:
                    self._pass.error(message, ex, back)

                if isinstance(message, OANNetworkComandShutdown):
                    break

        self._server.shutdown()
        asyncore.loop()
        log.info("Stop network worker %s" % self.name)


class OANNetwork:
    # Events
    on_receive = None
    on_send = None
    on_message = None
    on_error = None

    # Private variables

    # Will only have one worke due to asyncore.
    _worker = None
    _pass = None

    def __init__(self):
        self._pass = OANPassthru()
        self._worker = OANNetworkWorker(self._pass)
        self.on_message = self._pass.on_message
        self.on_error = self._pass.on_error

    def add_timer(self, timer):
        self._worker.add_timer(timer)

    def remove_timer(self, timer):
        self._worker.remove_timer(timer)

    def execute(self, message):
        self._pass.execute(message)

    def select(self, message):
       return self._pass.select(message)

    def get(self, message):
        for ret in self._pass.select(message):
            return ret

    def shutdown(self):
        self._pass.execute(OANNetworkComandShutdown())
        self._worker.join()
