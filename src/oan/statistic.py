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

    def __init__(self):
        self.out_current_queue_count = 0
        self.out_transfered = 0
        self.out_counter = 0
        self.in_current_queue_count = 0
        self.in_transfered = 0
        self.in_counter = 0
        self.start_time = datetime.utcnow()
        self.update_time = datetime.utcnow()

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

    def calculate(self):
        diff = self.update_time - self.start_time
        self.update_time = datetime.utcnow()

    def unserialize(self, data):
        self.out_transfered, self.out_counter, self.in_transfered, self.in_counter = data

    def serialize(self):
        return (self.out_transfered, self.out_counter, self.in_transfered, self.in_counter)

    def __str__(self):
        (utime, stime, cutime, cstime, elapsed_time) = os.times()
        return "out:[%sq][%sc][%sb] in:[%sq][%sc][%sb] cpu: %s, %s %s" % (self.out_current_queue_count,
                                                                          self.out_counter,
                                                                          self.out_transfered,
                                                                          self.in_current_queue_count,
                                                                          self.in_counter,
                                                                          self.in_transfered,
                                                                          utime, stime, cutime)


