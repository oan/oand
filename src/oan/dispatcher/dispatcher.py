#!/usr/bin/env python
"""
Dispatcher handles messages that are sent over the network or locally
in the application.

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
from oan.dispatcher.command import OANCommandShutdown


class OANMessageWorker(Thread):
    """
    A thread class that get messages from a OANPassthru queue. OANMessageWorker
    processes the messages and returns the result back through the OANPassthru.

    If a exception is raised in a message it will return through the OANPassthru
    an on_error event will be fired.

    OANMessageDispatcher starts several OANMessageWorker that gets messages
    from the same OANPassthru.
    """

    _passthru = None
    _dispatcher = None

    def __init__(self, dispatcher, passthru):
        Thread.__init__(self)
        self._dispatcher = dispatcher
        self._passthru = passthru
        Thread.start(self)

    def run(self):
        """
        Thread run method that will loop until it receives a shutdown message.
        """
        q = self._passthru

        log.info("Start message worker %s" % self.name)

        while True:
            # The thread will block to it gets a message from queue.
            (message, back) = q.get()
            try:
                ret = message.execute(self._dispatcher)
                self._passthru.result(ret, back)
            except Exception as ex:
                self._passthru.error(message, ex, back)

            if isinstance(message, OANCommandShutdown):
                # Put back shutdown message for other worker threads
                q.execute(message)
                break

        log.info("Stop message worker %s" % self.name)





class OANMessageDispatcher:
    """
    A dispatcher that processes messages and put them to several
    threads (OANMessageWorker).

    If you want a result back from the message, simply use "select"
    or "get" methods. The calling thread will wait until the response is sent
    back via OANPassthru.

    If you just want process a message without waiting for a return value, you
    can use the execute method.

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
    _passthru = None

    def __init__(self, config, node_manager, meta_manager, data_manager):
        self._passthru = OANPassthru()
        self.on_message = self._passthru.on_message
        self.on_error = self._passthru.on_error
        self._start()

    def execute(self, message):
        """
        Send a message to one of the workers, if a exception is raised
        on_error event will be fired.
        """
        self._passthru.execute(message)

    def select(self, message):
        """
        Send a message to one of the workers and wait for the result, the
        result is a generator. If you just want a single value use "get"
        method insted.
        """
        return self._passthru.select(message)

    def get(self, message):
        """
        Send a message to one of the workers and wait for a single value
        return.
        """
        for ret in self._passthru.select(message):
            return ret

    def shutdown(self):
        """
        Sends a shutdown message to stop all workers. Wait for the workers
        to finished.
        """
        self._passthru.execute(OANCommandShutdown())
        for worker in self._workers:
            worker.join()

    def _start(self):
        """
        Start all workers.
        TODO: make number of workers dynamic start a new if all are used, it a
        worker is idle for a period of time stop the worker.
        """
        for i in xrange(5):
            worker = OANMessageWorker(self, self._passthru)
            self._workers.append(worker)




