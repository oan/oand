#!/usr/bin/env python
'''


'''

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import time
import os
import thread

from datetime import datetime, timedelta

class OANNetworkNodeStatistic:
    out_transfered = None # total written kilobytes to other nodes
    out_counter = None # total messages write to other nodes

    in_transfered = None # total read kilobyte read from other nodes
    in_counter = None # total read messages from other nodes

    total_up_time = None # total cpu time user + kernel
    total_cpu_time = None # total up time

    update_time = None # time when statistic was updated
    start_time = None # when this node started
    cpu_time = None # cpu time user + kernel since start
    up_time = None # total up time since start

    def __init__(self):
        self.out_transfered = 0
        self.out_counter = 0
        self.in_transfered = 0
        self.in_counter = 0
        self.start_time = datetime.utcnow()
        self.update_time = datetime.utcnow()


    def add_in_transfered(self, bytes):
        self.in_transfered = self.in_transfered + bytes
        self.in_counter = self.in_counter + 1
        self.p()

    def add_out_transfered(self, bytes):
        self.out_transfered = self.out_transfered + bytes
        self.out_counter = self.out_counter + 1
        self.p()

    def p(self):
        (utime, stime, cutime, cstime, elapsed_time) = os.times()
        print "out:%s [%s] in:%s [%s] cpu: %s, %s %s" % (self.out_counter, self.out_transfered, self.in_counter, self.in_transfered, utime, stime, cutime)

    def calculate(self):
        diff = self.update_time - self.start_time
        self.update_time = datetime.utcnow()

    def unserialize(self, data):
        self.out_transfered, self.out_counter, self.in_transfered, self.in_counter = data

    def serialize(self):
        return (self.out_transfered, self.out_counter, self.in_transfered, self.in_counter)

