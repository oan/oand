#!/usr/bin/env python
"""
Executes messages/commands in the application.

"""

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import sys
from threading import Thread

from oan.util import log
from oan.passthru import OANPassthru
from oan.dispatcher.command import OANCommandShutdown


class OANDispatcherWorker(Thread):
    """
    A thread that executes messages on a OANPassthru queue.

    OANDispatcherWorker processes the messages and returns the result back
    through the OANPassthru.

    If a exception is raised in a message it will be returned through the
    OANPassthru, an on_error event will be fired.

    OANDispatcher starts several OANDispatcherWorker that gets messages
    from the same OANPassthru.

    """

    _passthru = None

    def __init__(self, passthru):
        Thread.__init__(self)
        self.name = "DISP-" + self.name.replace("Thread-", "")
        self._passthru = passthru
        Thread.start(self)

    def run(self):
        """
        Thread main loop executed until it receives a shutdown message.

        """
        passthru = self._passthru

        log.info("Start dispatcher worker %s" % self.name)

        while True:
            # The thread will block until it gets a message from queue.
            (message, back) = passthru.get()
            try:
                ret = message.execute()
                self._passthru.result(ret, back)

            # Catching too general exception Exception
            # pylint: disable=W0703
            #   We don't know the types of exceptions that on_error might
            #   raise, so catch them all and send them on the "back" queue
            #   for result method to handle.
            except Exception as ex:
                self._passthru.error(message, ex, back)

            if isinstance(message, OANCommandShutdown):
                # Put back shutdown message for other worker threads
                passthru.execute(message)
                break

        log.info("Stop dispatcher worker %s" % self.name)


class OANDispatcher:
    """
    Dispatches messages and commands to several worker threads.

    If you want a result back from the message, simply use "select"
    or "get" methods, The calling thread will wait until the response is sent
    back through OANPassthru.

    If you just want process a message without waiting for a return value, you
    can use the execute method.

    EVENTS:

    on_message  Callback event that will be triggered when a message is poped
                from the queue.

                Example:
                def got_message(self, message):
                    print "got message"

                on_message.append(got_message)

    on_error    Callback event that will be called when worker thread got
                any error, for example when the message execute raises an
                exception.

                Example:
                def got_error(self, message, exception):
                    print "got error", exception

                on_error.append(got_error)

    """

    # Events
    on_message = None
    on_error = None

    # Private variables
    _workers = []
    _passthru = None

    def __init__(self):
        self._passthru = OANPassthru()
        self.on_message = self._passthru.on_message
        self.on_error = self._passthru.on_error
        self._start()

    def shutdown(self):
        """
        Sends a shutdown message to stop all workers. Wait for the workers
        to finished.

        """

        self._passthru.execute(OANCommandShutdown())
        for worker in self._workers:
            worker.join()

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

    def _start(self):
        """
        Start all workers.

        """
        for i in xrange(5):
            worker = OANDispatcherWorker(self._passthru)
            self._workers.append(worker)
