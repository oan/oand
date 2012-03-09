#!/usr/bin/env python
'''
calculates a sleep time for a cpu limit.

'''

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from time import sleep, time
from os import times

class OANThrottle():
    uold = None
    sold = None
    cold = None

    unew = None
    snew = None
    cnew = None


    _span = 10 # seconds that the average is calulated on.
    _last = 0

    _sleep = 0

    @staticmethod
    def _set_old():
        t = time()
        if OANThrottle._last + OANThrottle._span < t:
            OANThrottle._last = t
            OANThrottle.uold, OANThrottle.sold, OANThrottle.cold, c, e = times()

    @staticmethod
    def _set_new():
        OANThrottle.unew, OANThrottle.snew, OANThrottle.cnew, c, e = times()

    @staticmethod
    def reset():
        OANThrottle._last = 0
        OANThrottle._sleep = 0

    @staticmethod
    def current():
        current = 0
        if OANThrottle.sold:
            OANThrottle._set_new()
            current = (float(OANThrottle.unew) - float(OANThrottle.uold)) / (time()-float(OANThrottle._last))

        OANThrottle._set_old()
        return current

    @staticmethod
    def calculate(max = 0.1):
        current = OANThrottle.current()
        if current > max:
            OANThrottle._sleep += 0.2
        else:
            OANThrottle._sleep -= 0.2

        if OANThrottle._sleep < 0.2:
            OANThrottle._sleep = 0

        return OANThrottle._sleep

    @staticmethod
    def throttle(max = 0.1):
        sleep(OANThrottle.calculate(max))
