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


    """

    """
    def execute(self, message):
        self.put((message, None))
        #log.debug(str(message))



    """

    """
    def select(self, message):
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


    """

    """
    def get(self):
        (message, back) = Queue.get(self)
        #log.debug(str(message))
        self.on_message(message)
        return (message, back)


    """

    """
    def error(self, message, ex, back):
        log.debug("Got error %s on %s " % (ex, message))
        self.on_error(message, ex)

        if (back):
            back.put(ex)
            back.put(None)

    """

    """
    def result(self, ret, back):
        if (back):
            if ret is not None:
                for rec in ret:
                    back.put(rec)

            back.put(None)
            log.debug(str(back.__class__))
