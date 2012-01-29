#!/usr/bin/env python
"""
Handle communication between threads.

"""

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from Queue import Queue

from oan.util import log
from oan.event import OANEvent


class OANPassthru(Queue):
    """
    Handle communication between threads.

    Safely communicate between threads. It will be used by OANDispatcher,
    OANDatabase and OANNetwork.

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

    def __init__(self):
        """Initialize all internal events/callbacks."""
        Queue.__init__(self)
        self.on_message = OANEvent()
        self.on_error = OANEvent()

    def execute(self, message):
        """
        Add a message to the internal queue.

        An execute will not return any result, it will just execute the message
        and then throw away the message and ignore any results.

        The back queue argument will be set to "None" and by that ignored by
        any passthru methods.

        """
        self.put((message, None))
        log.debug(str(message))

    def select(self, message):
        """
        Add a message to the internal queue and return the result from execute.

        A message will be added to the internal queue. A worker thread will
        pickup the message and process it. The result from the message will
        be returned back to this function. This function will then yield one
        item from the message result at a time.

        This method will continue to yield until the message adds "None" to
        the back queue or raises an exception.

        """
        back = Queue()
        self.put((message, back))
        log.debug(str(message))
        while True:
            ret = back.get()

            if isinstance(ret, Exception):
                raise ret

            if ret == None:
                break

            yield ret

    def get(self, block=True, timeout=None):
        """
        Called by worker to pop the first inserted message on the queue. (FIFO)

        Used by a worker thread to pop messages to process. The internal
        on_message callback will be called on the message.

        """
        (message, back) = Queue.get(self, block, timeout)
        log.debug(str(message))
        if not self.on_message.empty():
            self.on_message(message)
        return (message, back)

    def error(self, message, ex, back):
        """
        Called by worker if any error is found when executing a message.

        The internal on_error callback will be called for the error. The
        exception catched by the worker thread will be added to the back
        queue if this was a "select" message.

        """
        log.debug("Got error %s on %s " % (ex, message))

        try:
            if not self.on_error.empty():
                self.on_error(message, ex)

        # Catching too general exception Exception
        # pylint: disable=W0703
        #   We don't know the types of exceptions that on_error might
        #   raise, so catch them all and send them on the "back" queue
        #   for result method to handle.
        except Exception as ex2:
            if (back):
                back.put(ex2)

        if (back):
            back.put(ex)
            back.put(None)

    def result(self, ret, back):
        """
        Called by worker to move result from message to queue result.

        """
        # Method could be a function
        # pylint: disable=R0201
        #   The architecture is clearer if the is a method.
        if (back):
            if ret is not None:
                for rec in ret:
                    back.put(rec)

            back.put(None)
            log.debug(str(back.__class__))
