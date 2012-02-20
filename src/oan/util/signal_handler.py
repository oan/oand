#!/usr/bin/env python
"""
Test cases for util.daemon_base

Downloaded from
http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/

"""

__author__ = "martin.palmer@amivono.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer@amivono.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from datetime import datetime, timedelta
from signal import signal
from threading import Lock
from Queue import Queue, Empty

class OANTerminateInterrupt(Exception): pass
class OANStatusInterrupt(Exception): pass

class OANSignalTimer(object):
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

    def __init__(self, interval, callback, *args, **kwargs):
        self._interval = interval
        self._callback = callback
        self._args = args
        self._kwargs = kwargs
        self._calc_expire()

    @property
    def interval(self):
        return self._interval

    def check(self):
        """Execute callback if the timer has expired."""
        checked = datetime.utcnow()
        if (self._expires < checked):
            self._callback(*self._args, **self._kwargs)
            self._calc_expire()
            return True

        return False

    def _calc_expire(self):
        """Calculate and set the next time the cmd should be executed."""
        self._expires = datetime.utcnow() + timedelta(seconds = self._interval)


class OANSignalHandler:
    _lock = Lock()
    _dict =  {}
    _interrupts = {}
    _timers = []
    _queue = Queue()
    _timer_timeout = 60 * 12 * 24 * 365 # a year
    _timeout = None

    @staticmethod
    def wait(timeout = None):
        """
        Get must have a timeout to be inturrupted.
        """
        print "Waiting for interupts"
        while True:
            OANSignalHandler._check_timers()
            try:
                raise Queue.get(OANSignalHandler._queue, True, OANSignalHandler._timeout)
            except Empty:
                print "no signal in queue"


    @staticmethod
    def set(signum):
        with OANSignalHandler._lock:
            OANSignalHandler._interrupt_set(signum)


    @staticmethod
    def reset(signum):
        with OANSignalHandler._lock:
            OANSignalHandler._interrupt_reset(signum)

    @staticmethod
    def timer(interval, callback, *args, **kwargs):
        with OANSignalHandler._lock:
            if interval < OANSignalHandler._timeout:
                OANSignalHandler._timeout = interval

            OANSignalHandler._timers.append(
                OANSignalTimer(interval, callback, args, kwargs))

            sorted(OANSignalHandler._timers, key=lambda timer: timer.interval)

    @staticmethod
    def register(signum, interrupt):
        with OANSignalHandler._lock:
            OANSignalHandler._interrupts[signum] = interrupt
            signal(signum, OANSignalHandler._interrupt_occured)


    @staticmethod
    def _check_timers():
        with OANSignalHandler._lock:
            for timer in OANSignalHandler._timers:
                if not timer.check():
                    break

    @staticmethod
    def _interrupt_occured(signum, frame):
        with OANSignalHandler._lock:
            OANSignalHandler._interrupt_set(signum)


    @staticmethod
    def _interrupt_set(signum):
        if signum not in OANSignalHandler._dict:
            OANSignalHandler._dict[signum] = True
            Queue.put(OANSignalHandler._queue, OANSignalHandler._interrupts[signum])


    @staticmethod
    def _interrupt_reset(signum):
        if signum in OANSignalHandler._dict:
            del OANSignalHandler._dict[signum]
