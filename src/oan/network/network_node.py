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
from uuid import UUID

from oan.heartbeat import OANHeartbeat
from oan.statistic import OANNetworkNodeStatistic
from oan.util.decorator.synchronized import synchronized


class OANNetworkNodeState(object):
    """States a network node connection can be in."""
    DISCONNECTED, CONNECTING, CONNECTED = range(1, 4)


class OANNetworkNode:
    """Thread safe network node representation."""

    # All messages that should be sent to the node through the network.
    out_queue = None

    # A unique UUID representing this node.
    _oan_id = None

    # A non unique name which the node is known as.
    _name = None

    # The external ip-number or domain for node.
    _host = None

    # The port on which the node listening for oan connections.
    _port = None

    # A blocked node can't be reached from internet through the firewall.
    _blocked = None

    # The current connection state of bridge connection between
    # local node and this remote node.
    _state = None

    _heartbeat = None
    _statistic = None

    # Synchronize the node instance when accessed by several threads.
    _lock = None

    def __init__(self, oan_id):

        # I don't like this autoconvert things :-)
        if isinstance(oan_id, UUID):
            self._oan_id = oan_id
        else:
            self._oan_id = UUID(oan_id)

        self._state = OANNetworkNodeState.DISCONNECTED
        self._heartbeat = OANHeartbeat()
        self.out_queue = Queue(1000)
        self._lock = Lock()

    @classmethod
    def create(cls, oan_id, host, port, blocked):
        """Create a useable node."""
        obj = cls(oan_id)
        obj._host, obj._port, obj._blocked = host, int(port), blocked
        obj._statistic = OANNetworkNodeStatistic()
        return obj

    @synchronized
    def update(self,
        name=None, host=None, port=None,
        blocked=None, state=None, heartbeat=None
    ):
        """
        Used to update a node in a threadsafe way.

        Example:
        node.update(port=1338)

        """
        if name != None:
            self._name = name
        if host != None:
            self._host = host
        if port != None:
            self._port = int(port)
        if blocked != None:
            self._blocked = blocked
        if state != None:
            self._state = state
        if heartbeat != None:
            self._heartbeat.set_value(heartbeat)

    @property
    def oan_id(self):
        """A unique UUID representing this node."""
        return self._oan_id

    @synchronized
    def get(self):
        """Return a tuple with all node values."""
        return (
            self._name,
            self._host,
            self._port,
            self._blocked,
            self._state,
            self._heartbeat.value
        )

    @synchronized
    def unserialize(self, data):
        """Recreate node from dict produced by serialize."""
        self._name = data["name"]
        self._host = data["host"]
        self._port = data["port"]
        self._blocked = data["blocked"]
        self._heartbeat.set_value(data["heartbeat"])
        self._state = OANNetworkNodeState.DISCONNECTED
        self._statistic = OANNetworkNodeStatistic()
        self._statistic.unserialize(data["statistic"])

    @synchronized
    def serialize(self):
        """
        Return a dict that can be used to recreate this node with serialize.

        """
        return {
            "name": self._name,
            "host": self._host,
            "port": self._port,
            "blocked": self._blocked,
            "heartbeat": self._heartbeat.value,
            "statistic": self._statistic.serialize()
        }

    @synchronized
    def __str__(self):
        return 'OANNetworkNode(%s, %s, %s) queue(%s) hb(%s) stat(%s)' % (
            self._oan_id, self._host, self._port,
            self.out_queue.qsize(),
            self._heartbeat.time,
            self._statistic
        )

    def send(self, message):
        """
        Send a message to this node.

        The message will be added to an internal queue that are polled by
        the network worker.

        """
        self.out_queue.put(message)

    @synchronized
    def is_disconnected(self):
        """The network connection to this node is not active."""
        return self._state == OANNetworkNodeState.DISCONNECTED

    @synchronized
    def has_heartbeat_state(self, state):
        """What is the known online state of the node."""
        return self._heartbeat.has_state(state)
