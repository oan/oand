#!/usr/bin/env python
"""

"""

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from threading import Thread, Lock
from Queue import Queue

from oan.util import log
from oan.passthru import OANPassthru
from oan.message import OANMessageShutdown

class OANMessageDispatcher:
    """

    """

    config = None
    node_manager = None
    meta_manager = None
    data_manager = None

    """
    Event fired when message is retrivied from queue before message.execute is
    called.

    Example:
        def got_message(self, message):
            pass

        xxx.on_message.append(got_message)

    """
    on_message = None

    """
    Event fired when a exception is raised in message.execute.

    Example:
        def got_error(self, message, ex):
            pass

        xxx.on_error.append(got_error)
    """
    on_error = None

    _workers = []
    _pass = None

    def __init__(self, config):
        self._pass = OANPassthru()
        self.on_message = self._pass.on_message
        self.on_error = self._pass.on_error
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

class OANMessageWorker(Thread):
    """

    """
    _pass = None

    def __init__(self, passthru):
        Thread.__init__(self)
        self._pass = passthru
        Thread.start(self)

    def run(self):
        q = self._pass

        log.info("Start message worker %s" % self.name)

        while True:
            (message, back) = q.get()
            try:
                ret = message.execute()
                self._pass.result(ret, back)
            except Exception as ex:
                self._pass.error(message, ex, back)

            if isinstance(message, OANMessageShutdown):
                # Put back shutdown message for other worker threads
                q.execute(message)
                break

        log.info("Stop message worker %s" % self.name)
