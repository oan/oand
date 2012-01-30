#!/usr/bin/env python
"""
Thread safe network node representation.

"""

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from threading import Lock
from Queue import Queue

from oan.heartbeat import OANHeartbeat
from oan.statistic import OANNetworkNodeStatistic


class OANNetworkNodeState(object):
    """The different states a network node can be in.
    TODO uppercase"""
    connecting, connected, disconnected = range(1, 4)


class OANNetworkNode:
    """
    Thread safe network node representation.

    """
    oan_id = None
    name = None
    host = None
    port = None

    # A blocked node can't be reached from internet through the firewall.
    blocked = None

    state = None

    heartbeat = None
    statistic = None

    out_queue = None
    _lock = None

    def __init__(self, oan_id):
        self.oan_id = oan_id
        self.state = OANNetworkNodeState.disconnected
        self.heartbeat = OANHeartbeat()
        self.out_queue = Queue(1000)
        self._lock = Lock()

    @classmethod
    def create(cls, oan_id, host, port, blocked):
        obj = cls(oan_id)
        obj.host, obj.port, obj.blocked = host, port, blocked
        obj.statistic = OANNetworkNodeStatistic()
        return obj

    def update(self, host = None, port = None, blocked = None, state = None):
        #with self._lock:
        #TODO
        # with lock
        #   if host not None:
        #       self.host = host
        pass

    def get(self):
        with self._lock:
            return (self.host, self.port, self.blocked, self.state)

    def send(self, message):
        self.out_queue.put(message)

    def is_disconnected(self):
        with self._lock:
            return self.state == OANNetworkNodeState.disconnected

    def unserialize(self, data):
        with self._lock:
            self.host, self.port, self.blocked, subdata = data
            self.statistic = OANNetworkNodeStatistic()
            self.statistic.unserialize(subdata)

    def serialize(self):
        with self._lock:
            return(self.host, self.port, self.blocked, self.statistic.serialize())

    def __str__(self):
        with self._lock:
            return 'OANNetworkNode(%s, %s, %s) queue(%s) hb(%s) stat(%s)' % (
                self.oan_id, self.host, self.port,
                self.out_queue.qsize(),
                self.heartbeat.time,
                self.statistic
            )
