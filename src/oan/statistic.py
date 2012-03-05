#!/usr/bin/env python
'''


'''

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import os
from datetime import datetime

class OANNetworkMessageStatistic:
    sent_time = None
    out_time = None
    out_count = None
    in_count = None
    in_time = None

    def __init__(self):
        self.sent_time = None
        self.out_time = None
        self.out_count = 0
        self.in_time = None
        self.in_count = 0


    def _get_time(self, t):
        if t is None:
            return '---------------'
        else:
            return str(t)[11:]

    def __str__(self):
        return "sent[%s] out[%s][%s] in[%s][%s]" % (self._get_time(self.sent_time),
                                                        str(self.out_count).rjust(4, '0'),
                                                        self._get_time(self.out_time),
                                                        str(self.in_count).rjust(4, '0'),
                                                        self._get_time(self.in_time))


class OANNetworkNodeStatistic:
    out_transfered = None # total written kilobytes to other nodes
    out_counter = None # total messages write to other nodes
    out_max_queue_count = None # max number of total messages in out_queue
    out_current_queue_count = None # current number of queued messages

    in_transfered = None # total read kilobyte read from other nodes
    in_counter = None # total read messages from other nodes
    in_max_queue_count = None # max number of total messages in in_queue
    in_current_queue_count = None # current number of queued messages

    total_up_time = None # total cpu time user + kernel
    total_cpu_time = None # total up time

    update_time = None # time when statistic was updated
    start_time = None # when this node started
    cpu_time = None # cpu time user + kernel since start
    up_time = None # total up time since start

    _messages = None # holds statistic for diffrent messages

    def __init__(self):
        self.out_current_queue_count = 0
        self.out_transfered = 0
        self.out_counter = 0
        self.in_current_queue_count = 0
        self.in_transfered = 0
        self.in_counter = 0
        self.start_time = datetime.utcnow()
        self.update_time = datetime.utcnow()
        self._messages = {}

    def add_message_statistic(self, key,
            sent_time = False, out_time = False,
            in_time = False):

        current = self.get_message_statistic(key)

        if sent_time:
            current.sent_time = datetime.utcnow()
        elif out_time:
            current.out_time = datetime.utcnow()
            current.out_count += 1
        elif in_time:
            current.in_time = datetime.utcnow()
            current.in_count += 1

    def get_message_statistic(self, key):
        if not key in self._messages:
            current = OANNetworkMessageStatistic()
            self._messages[key] = current
        else:
            current = self._messages[key]

        return current

    def add_in_transfered(self, bytes):
        self.in_transfered = self.in_transfered + bytes
        self.in_counter = self.in_counter + 1

    def add_out_transfered(self, bytes):
        self.out_transfered = self.out_transfered + bytes
        self.out_counter = self.out_counter + 1

    def out_queue_inc(self):
        self.out_current_queue_count = self.out_current_queue_count+1

    def out_queue_dec(self):
        self.out_current_queue_count = self.out_current_queue_count-1

    def in_queue_inc(self):
        self.in_current_queue_count = self.in_current_queue_count+1

    def in_queue_dec(self):
        self.in_current_queue_count = self.in_current_queue_count-1

    #def calculate(self):
        #diff = self.update_time - self.start_time
        #self.update_time = datetime.utcnow()

    def unserialize(self, data):
        self.out_transfered, self.out_counter, self.in_transfered, self.in_counter = data

    def serialize(self):
        return (self.out_transfered, self.out_counter, self.in_transfered, self.in_counter)

    def __str__(self):
        (utime, stime, cutime, cstime, elapsed_time) = os.times()
        s = ""
        for name, stat in self._messages.items():
            s += "%s%s\n" % (name.ljust(30,' '), stat)

        return "%sout:[%sq][%sc][%sb] in:[%sq][%sc][%sb] cpu: %s, %s %s \n%s\n" % (
            "Total".ljust(30, ' '),
            self.out_current_queue_count,
            str(self.out_counter).rjust(4,'0'),
            self.out_transfered,
            self.in_current_queue_count,
            str(self.in_counter).rjust(4,'0'),
            self.in_transfered,
            utime, stime, cutime, s)


