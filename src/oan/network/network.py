#!/usr/bin/env python
"""
Network thread that handles all the network traffic

"""

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


class OANNetworkTimer(object):
    """
    Execute a callback function every X seconds.

    check() should be executed every second to be able to internally execute
    callbacks that has an expired timer.

    """
    _interval = None
    _callback = None
    _args = None
    _kwargs = None

    _expires = None

    def __init__(self, sec, callback, *args, **kwargs):
        self._interval = sec
        self._callback = callback
        self._args = args
        self._kwargs = kwargs

        self._calc_expire()

    def check(self):
        """Execute callback if the timer has expired."""
        checked = datetime.utcnow()
        if (self._expires < checked):
            self._callback(*self._args, **self._kwargs)
            self._calc_expire()

    def _calc_expire(self):
        """Calculate and set the next time the cmd should be executed."""
        self._expires = datetime.utcnow() + timedelta(seconds = self._interval)


class OANNetworkWorker(Thread):
    """
    Handles the main network loop.

    Polls the network passthru queue for new commands/messages that needs
    to be executed.

    Polls the network queue through asyncore for new connections and sends
    them internally in asyncore code to the OANListen object.

    Controll if OANNetworkTimer callbacks should be executed.

    """

    # Private variables
    _timers = None
    _pass = None
    _server = None

    def __init__(self, passthru):
        Thread.__init__(self)
        self.name = "NETW-" + self.name.replace("Thread-", "")

        self._server = OANServer()
        self._pass = passthru
        self._timers = []
        Thread.start(self)

    def add_timer(self, timer):
        """Add a OANNetworkTimer to be executed by the main network loop."""
        self._timers.append(timer)

    def remove_timer(self, timer):
        """Remove a OANNetworkTimer from the main network loop."""
        self._timers.remove(timer)

    def run(self):
        """Main network loop"""
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
    """
    Handle communication between nodes through commands and messages.

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

    # TODO: Not implemented.
    #on_receive = None
    #on_send = None

    # Private variables

    # Will only have one worker because only one asyncore.loop can exist.
    _pass = None
    _worker = None

    def __init__(self):
        self._pass = OANPassthru()
        self._worker = OANNetworkWorker(self._pass)
        self.on_message = self._pass.on_message
        self.on_error = self._pass.on_error

    def add_timer(self, timer):
        """Add a OANNetworkTimer to be executed by the main network loop."""
        self._worker.add_timer(timer)

    def remove_timer(self, timer):
        """Remove a OANNetworkTimer from the main network loop."""
        self._worker.remove_timer(timer)

    def execute(self, command):
        """Execute a command via worker thread."""
        self._pass.execute(command)

    def select(self, command):
        """Execute a command via worker thread, return yielded result."""
        return self._pass.select(command)

    def get(self, command):
        """Execute a command via worker thread, return first row of result."""
        for ret in self._pass.select(command):
            return ret

    def shutdown(self):
        """Shutdown the network communication and all it's threads."""
        self._pass.execute(OANNetworkComandShutdown())
        self._worker.join()
        return True
