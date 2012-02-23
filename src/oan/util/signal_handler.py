#!/usr/bin/env python
"""

"""

__author__ = "martin.palmer@amivono.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer@amivono.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from os import kill, getpid
from time import sleep
from signal import signal
from threading import Lock

class OANTerminateInterrupt(Exception): pass
class OANStatusInterrupt(Exception): pass

class OANSignalHandler:
    """
    Handels OS-signals

    Example 1:
        OANSignalHandler.register(SIGINT, OANTerminateInterrupt())
        OANSignalHandler.register(SIGINFO, OANStatusInterrupt())

        while True:
            try:
                OANSignalHandler.wait()
            except OANTerminateInterrupt:
                sys.exit(0)
            except OANStatusInterrupt:
                print "is running"
                OANSignalHandler.reset(SIGINFO)


    Example 2:
        remember to deactivated the signal handler so not another signal
        is fired during handeling the first one.

        OANSignalHandler.register(SIGINT, OANTerminateInterrupt())
        OANSignalHandler.register(SIGINFO, OANStatusInterrupt())

        while True:
            try:
                try:
                    OANSignalHandler.activate()
                    in = raw_input('--> ')
                finally:
                    OANSignalHandler.deactivated()

            except OANTerminateInterrupt:
                print "Exit"
                sys.exit(0)
            except OANStatusInterrupt:
                print "Running"
                OANSignalHandler.reset(SIGINFO)

    """


    _lock = Lock()
    _dict =  {}
    _interrupts = {}
    _sleep = 60 * 12 * 24 * 365 # a year
    _activated = False

    @staticmethod
    def wait():
        """
        Will sleep forever until a signal occured, if you want your own loop
        just activate the signal handler inside a try catch statement.
        """
        #print "Waiting for interupts"
        try:
            OANSignalHandler.activate()
            while True:
                sleep(OANSignalHandler._sleep)
        except Exception, e:
            #print "got interrupt"
            raise e
        finally:
            OANSignalHandler.deactivate()

    @staticmethod
    def activate():
        """
        activate the signal handler, if a signal occurs it will be raised.
        """

        with OANSignalHandler._lock:
            OANSignalHandler._activated = True

            # check if there are any interrupts that should be raised.
            for signum, state in OANSignalHandler._dict.items():
                if not state:
                    OANSignalHandler._interrupt_raise(signum)

    @staticmethod
    def deactivate():
        """
        if the signal handler is deactivated, all signals will be delayed until
        its activated again. if a interrupt has been raised, the signal handler
        is deactivated and need to be activated again.

        """

        with OANSignalHandler._lock:
            OANSignalHandler._activated = False

    @staticmethod
    def fire(signum):
        """
        fires a signal to current pid
        """
        kill(getpid(), signum)

    @staticmethod
    def set(signum):
        """
        set the signal and fires a interrupt exception.
        """
        with OANSignalHandler._lock:
            OANSignalHandler._interrupt_set(signum)


    @staticmethod
    def reset(signum):
        """
        a interrupt exception is fired just once if it's not reset.
        """
        with OANSignalHandler._lock:
            OANSignalHandler._interrupt_reset(signum)


    @staticmethod
    def register(signum, interrupt):
        """
        register a interrupt with a signal number.
        """
        with OANSignalHandler._lock:
            OANSignalHandler._interrupts[signum] = interrupt
            signal(signum, OANSignalHandler._interrupt_occured)


    @staticmethod
    def _interrupt_occured(signum, frame):
        """
        when the OS is sending a signal this function will be called.
        """
        with OANSignalHandler._lock:
            OANSignalHandler._interrupt_set(signum)

    @staticmethod
    def _interrupt_set(signum):
        """
        set a signal to be fired. it may be delayed if the signal handler
        is deactivated.
        """
        if signum not in OANSignalHandler._dict:
            if OANSignalHandler._activated:
                OANSignalHandler._interrupt_raise(signum)
            else:
                OANSignalHandler._interrupt_delay(signum)

    @staticmethod
    def _interrupt_reset(signum):
        """
        reset the signal so it can be fired once again.
        """
        if signum in OANSignalHandler._dict:
            del OANSignalHandler._dict[signum]


    @staticmethod
    def _interrupt_raise(signum):
        """
        raise a interrupt and deactivate the signal handler, we don't want
        an other interrupt be fired before we handled the first one.
        """
        OANSignalHandler._dict[signum] = True
        OANSignalHandler._activated = False
        raise OANSignalHandler._interrupts[signum]


    @staticmethod
    def _interrupt_delay(signum):
        """
        delay the interrupt until the signal handler is activated
        """
        OANSignalHandler._dict[signum] = False

