#!/usr/bin/env python
'''
LogCounter

'''

__author__ = "martin@amivono.com, daniel@amivono.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin@amivono.com, daniel@amivono.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"


import time


class LogCounter():

    class LogEntry():
        counter = None
        last_elapsed = None
        total_elapsed = None
        min_elapsed = None
        max_elapsed = None

        def __init__(self):
            self.counter = 0
            self.last_elapsed = 0
            self.total_elapsed = 0
            self.min_elapsed = None
            self.max_elapsed = 0

        def __str__(self):
            return ("counter:{0:>6}, total:{1:>7.4f}, avg:{2:>7.4f}, " +
                    "min:{3:>7.4f}, max:{4:>7.4f}").format(
                    self.counter, self.total_elapsed,
                    self.total_elapsed / (self.counter or 1),
                    self.min_elapsed, self.max_elapsed
            )

    _entries = {}


def clear():
    LogCounter._entries = {}


def begin(key):
    if key not in LogCounter._entries:
        entry = LogCounter.LogEntry()
        LogCounter._entries[key] = entry
    else:
        entry = LogCounter._entries[key]

    entry.start = time.time()


def end(key):
    entry = LogCounter._entries[key]
    entry.counter += 1
    entry.last_elapsed = (time.time() - entry.start)
    entry.total_elapsed += entry.last_elapsed
    entry.max_elapsed = max(entry.last_elapsed, entry.max_elapsed)
    if entry.min_elapsed == None:
        entry.min_elapsed = entry.last_elapsed
    else:
        entry.min_elapsed = min(entry.last_elapsed, entry.min_elapsed)


def hit(key):
    begin(key)
    end(key)


def result():

    ret = ""
    keys = LogCounter._entries.keys()
    keys.sort()

    for key in keys:
        ret += "\n{0:<30} -> {1}".format(key, str(LogCounter._entries[key]))

    return ret

