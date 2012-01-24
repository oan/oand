#!/usr/bin/env python
'''


'''

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import asyncore
import socket
import time
import os
import datetime

from uuid import UUID
from Queue import Queue

from oan.util import log
from oan.heartbeat import OANHeartbeat
from oan.statistic import OANNetworkNodeStatistic


class OANNetworkNodeState:
    #TODO uppercase
    connecting, connected, disconnected = range(1, 4)

"""
TODO
    All members should be private and we should use get/set which are thread safe.

    def get()
        return (sdf), sadf ,sadf, )

    def set(oan_id, host, port, blocked)
        with self._lock:
            self.name = name

"""
class OANNetworkNode:
    oan_id = None
    name = None
    port = None
    host = None
    state = None
    blocked = None # if server is listen or its blocked by router or firewall.

    heartbeat = None
    statistic = None

    out_queue = None

    def __init__(self, oan_id):
        self.state = OANNetworkNodeState.disconnected
        self.heartbeat = OANHeartbeat()
        self.out_queue = Queue(1000)
        self.oan_id = oan_id

    @classmethod
    def create(cls, oan_id, host, port, blocked):
        obj = cls(oan_id)
        obj.host, obj.port, obj.blocked = host, port, blocked
        obj.statistic = OANNetworkNodeStatistic()
        return obj

    def update(self, host = None, port = None, blocked = None, state = None):
        #TODO
        # with lock
        #   if host not None:
        #       self.host = host
        pass

    def get(self):
        # with Lock
        return (self.host, self.port, self.blocked, self.state)

    def send(self, message):
        self.out_queue.put(message)

    def is_disconnected(self):
        # with lock
        return self.state == OANNetworkNodeState.disconnected

    def unserialize(self, data):
        self.host, self.port, self.blocked, subdata = data
        self.statistic = OANNetworkNodeStatistic()
        self.statistic.unserialize(subdata)

    def serialize(self):
        return(self.host, self.port, self.blocked, self.statistic.serialize())

    def __str__(self):
        return 'OANNetworkNode(%s, %s, %s) (queue: %s) (%s) (%s)' % (
            self.oan_id, self.host, self.port,
            self.out_queue.qsize(),
            self.heartbeat.time, self.statistic
        )
