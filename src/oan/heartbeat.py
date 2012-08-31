#!/usr/bin/env python
"""
Representing a heartbeat "timestamp".

"""

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from datetime import datetime, timedelta

class OANHeartbeat(object):
    """
    Representing a heartbeat "timestamp"

    >>> hb = OANHeartbeat()
    >>> hb.is_idle()
    True
    >>> hb.is_idle()
    True
    >>> hb.is_expired()
    True
    >>> hb.is_offline()
    True
    >>> hb.is_dead()
    False

    """
    _value = None

    # Constants used with has_state()
    IDLE, NOT_IDLE, EXPIRED, NOT_EXPIRED, OFFLINE, NOT_OFFLINE, DEAD, NOT_DEAD = range(1, 9)

    IDLE_MIN = 5 # test value 0.1
    EXPIRED_MIN = 10 # test value 0.2
    OFFLINE_MIN = 50
    DEAD_MIN = 525600

    # ISO 8601 format
    _date_fmt = "%Y-%m-%dT%H:%M:%SZ"
    _time_fmt = "%H:%M:%S"

    def __init__(self,  last_heartbeat = None):
        if (last_heartbeat is None):
            self.set_offline()
        else:
            self.set_value(last_heartbeat)

    def __str__(self):
        return str(self._value)

    def get_value(self):
        return self._value.strftime(self._date_fmt)

    def set_value(self, datetime_str):
        self._value = datetime.strptime(datetime_str,  self._date_fmt)
        if (not self._value):
            raise Exception('Not valid date.' + datetime_str)

    value = property(get_value, set_value)

    def get_time(self):
        return self._value.strftime(self._time_fmt)

    time = property(get_time)

    def touch(self):
        self._value = datetime.utcnow()
        return self.get_value()

    def set_idle(self):
        self._value = (datetime.utcnow() - timedelta(minutes = self.IDLE_MIN, seconds = 1))

    def set_expired(self):
        self._value = (datetime.utcnow() - timedelta(minutes = self.EXPIRED_MIN, seconds = 1))

    def set_offline(self):
        self._value = (datetime.utcnow() - timedelta(minutes = self.OFFLINE_MIN, seconds = 1))

    def set_dead(self):
        self._value = (datetime.utcnow() - timedelta(minutes = self.DEAD_MIN, seconds = 1))

    def _is_touched(self, min):
        """
        Check if the heartbeat has been touched within MIN minutes.

        min - Number of minutes the heatbeat is valid.)

        """
        expired_date = datetime.utcnow() - timedelta(minutes = min)
        if (expired_date < self._value):
            return False

        return True


    def is_idle(self):
        """
        The heartbeat has not been touched for 1 minute.

        >>> hb = OANHeartbeat()
        >>> hb.is_idle()
        True

        """
        return self._is_touched(self.IDLE_MIN)

    def is_expired(self):
        """
        The heartbeat has not been touched for 5 minutes.

        The node needs to be verified if it's still alive.

        >>> hb = OANHeartbeat()
        >>> hb.is_expired()
        True

        """
        return self._is_touched(self.EXPIRED_MIN)

    def is_offline(self):
        """
        The heartbeat has not been touched for 10 minutes.

        The node is probably offline.

        >>> hb = OANHeartbeat()
        >>> hb.is_offline()
        True

        """
        return self._is_touched(self.OFFLINE_MIN)

    def is_dead(self):
        """
        The heartbeat has not been touched for 10 days.

        The node is probably dead.

        >>> hb = OANHeartbeat()
        >>> hb.is_dead()
        False

        """
        return self._is_touched(self.DEAD_MIN)

    def has_state(self, state):
        """Check if heartbeat is in state."""

        if state == OANHeartbeat.IDLE:
            return self.is_idle()

        elif state == OANHeartbeat.NOT_IDLE:
            return not self.is_idle()

        elif state == OANHeartbeat.EXPIRED:
            return self.is_expired()

        elif state == OANHeartbeat.NOT_EXPIRED:
           return not self.is_expired()

        elif state == OANHeartbeat.OFFLINE:
            return self.is_offline()

        elif state == OANHeartbeat.NOT_OFFLINE:
            return not self.is_offline()

        elif state == OANHeartbeat.DEAD:
            return self.is_dead()

        elif state == OANHeartbeat.NOT_DEAD:
            return not self.is_dead()

    def __cmp__(self, other):
        left = self._value

        if isinstance(other, OANHeartbeat):
            right = other._value
        else:
            right = OANHeartbeat(other)._value

        if left < right:
            return -1
        elif left > right:
            return 1
        else:
            return 0
