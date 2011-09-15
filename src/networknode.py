#!/usr/bin/env python
'''
Representaion of a network node.

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from datetime import datetime, timedelta

class NetworkNode():
    _node_id = None
    _name = None
    _domain_name = None
    _port = None
    _last_heartbeat = None


    _date_fmt = "%Y-%m-%d %H:%M:%S"

    def __init__(self, name, domain_name, port):
        self._node_id = name
        self._name = name
        self._domain_name = domain_name
        self._port = port

        self._last_heartbeat = datetime.strptime("2006-06-06 06:06:06",
                                                 self._date_fmt)

    def get_id(self):
        return self._node_id

    def get_name(self):
        return self._name

    def get_domain_name(self):
        return self._domain_name

    def get_port(self):
        return self._port

    def set_last_heartbeat(self, datetime_str):
        self._last_heartbeat = datetime.strptime(datetime_str,  self._date_fmt)

    def touch_last_heartbeat(self):
        self._last_heartbeat = datetime.utcnow()

    def get_last_heartbeat(self):
        return self._last_heartbeat.strftime(self._date_fmt)

    def get_connection_url(self):
        return self.get_domain_name() + ':' + self.get_port()

    def is_heartbeat_expired(self, min = 5):
        '''
        Check if the heartbeat has expired.

        min - Number of minutes the heatbeat is valid.

        '''
        if (self._last_heartbeat):
            expire_date = datetime.utcnow() - timedelta(minutes = min)
            if (expire_date < self._last_heartbeat):
                return False

        return True

    def is_node_inactive(self):
        return self.is_heartbeat_expired(10)

    def is_valid(self):
        if (self.get_name() and
            self.get_domain_name() and
            self.get_port()):
            return True
        else:
            return False
