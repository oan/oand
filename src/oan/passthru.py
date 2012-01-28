#!/usr/bin/env python
"""
Safely communicate between threads. It will be used by OANDispatcher,
OANDatabase and OANNetwork.

"""

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import time
from Queue import Queue

from oan.util import log
from oan.event import OANEvent

class OANPassthru(Queue):

    """ Event """
    """
        use:

        def got_message(self, message):
            print "got message"

        on_message += [got_message]
    """
    on_message = None


    """
        use:

        def got_error(self, message, exception):
            print "got error", exception

        on_error += [got_error]
    """
    on_error = None

    def __init__(self):
        Queue.__init__(self)
        self.on_message = OANEvent()
        self.on_error= OANEvent()


    def execute(self, message):
        """
        Put a message on queue, it will not wait for a return value. Sets the
        back queue to "None"
        """
        self.put((message, None))
        #log.debug(str(message))



    def select(self, message):
        """
        Put a message on queue, it will wait for the message to be executed
        and passes the return values back. If it's a exception it will raise
        the exception to the calling thread.
        """
        back = Queue()
        self.put((message, back))
        #log.debug(str(message))
        while True:
            ret=back.get()

            if isinstance(ret, Exception):
                raise ret

            if ret == None:
                break

            yield ret


    def get(self):
        """
        When a OANMessageWorker picks a message from queue fire
        the on_message event.
        """
        (message, back) = Queue.get(self)
        #log.debug(str(message))
        self.on_message(message)
        return (message, back)


    def error(self, message, ex, back):
        """
        A message raised an exception, fire the on_error event and pass the
        exception back to the calling thread. "None" on the back queue means
        no more result.
        """
        log.debug("Got error %s on %s " % (ex, message))
        self.on_error(message, ex)

        if (back):
            back.put(ex)
            back.put(None)

    def result(self, ret, back):
        """
        If the calling thread is waiting for a response pass it back. "None"
        on the back queue means no more result.
        """
        if (back):
            if ret is not None:
                for rec in ret:
                    back.put(rec)

            back.put(None)
            log.debug(str(back.__class__))
