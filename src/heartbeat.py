#!/usr/bin/env python
'''
Representaion a heartbeat "timestamp".

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from datetime import datetime, timedelta

class HeartBeat(object):
    _value = None

    EXPIRE_MIN = 5
    INACTIVE_MIN = 10
    DEAD_MIN = 525600

    # ISO 8601 format
    _date_fmt = "%Y-%m-%dT%H:%M:%SZ"

    def __init__(self,  last_heartbeat = "2006-06-06T06:06:06Z"):
        self.set_value(last_heartbeat)

    def get_value(self):
        return self._value.strftime(self._date_fmt)

    def set_value(self, datetime_str):
        self._value = datetime.strptime(datetime_str,  self._date_fmt)
        if (not self._value):
            raise Exception('Not valid date.' + datetime_str)

    value = property(get_value, set_value)

    def touch(self):
        self._value = datetime.utcnow()
        return self.get_value()

    def set_expired(self):
        self._value = (datetime.utcnow() - timedelta(minutes = self.EXPIRE_MIN + 1))

    def set_inactive(self):
        self._value = (datetime.utcnow() - timedelta(minutes = self.INACTIVE_MIN + 1))

    def set_dead(self):
        self._value = (datetime.utcnow() - timedelta(minutes = self.DEAD_MIN + 1))

    def _is_expired(self, min):
        '''
        Check if the heartbeat has expired.

        If it has expired we haven't touched it for last MIN minutes.

        min - Number of minutes the heatbeat is valid.

        '''
        expire_date = datetime.utcnow() - timedelta(minutes = min)
        if (expire_date < self._value):
            return False

        return True

    def is_expired(self):
        '''
        The heartbeat has not been touched for 5 minutes.

        The node needs to be verified if it's still alive.

        '''
        return self._is_expired(self.EXPIRE_MIN)

    def is_inactive(self):
        '''
        The heartbeat has not been touched for 10 minutes.

        The node is probably offline.

        '''
        return self._is_expired(self.INACTIVE_MIN)

    def is_dead(self):
        '''
        The heartbeat has not been touched for 10 days.

        The node is probably dead.

        '''
        return self._is_expired(self.DEAD_MIN)
