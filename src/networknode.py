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

    # ISO 8601 format
    _date_fmt = "%Y-%m-%dT%H:%M:%SZ"

    def __init__(self, name, domain_name, port, last_heartbeat = "2006-06-06T06:06:06Z"):
        self._node_id = name
        self._name = name
        self._domain_name = domain_name
        self._port = port

        self.set_last_heartbeat(last_heartbeat)

    @classmethod
    def create_from_dict(cls, args):
        return cls (
            args['name'],
            args['domain_name'],
            args['port'],
            args['last_heartbeat'])

    def get_dict(self):
        param = {}
        param['node_id'] = self.get_id()
        param['name'] = self.get_name()
        param['domain_name'] = self.get_domain_name()
        param['port'] = self.get_port()
        param['last_heartbeat'] = self.get_last_heartbeat()
        return param

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
        return self.get_last_heartbeat()

    def get_last_heartbeat(self):
        return self._last_heartbeat.strftime(self._date_fmt)

    def get_connection_url(self):
        return self.get_domain_name() + ':' + self.get_port()

    def is_heartbeat_expired(self, min = 5):
        '''
        Check if the heartbeat has expired.

        If it has expired we haven't done any heartbeat requests to it during
        the last 5 minutes.

        min - Number of minutes the heatbeat is valid.

        '''
        if (self._last_heartbeat):
            expire_date = datetime.utcnow() - timedelta(minutes = min)
            if (expire_date < self._last_heartbeat):
                return False

        return True

    def is_node_inactive(self):
        '''
        This node has not answered to any heartbeat requests for 10 minutes.

        The node is probably offline.

        '''
        return self.is_heartbeat_expired(10)

    def is_node_expired(self):
        '''
        This node has not answered to any heartbeat requests for 10 days.

        '''
        return self.is_heartbeat_expired(525600)

    def is_valid(self):
        if (self.get_name() and
            self.get_domain_name() and
            self.get_port()):
            return True
        else:
            return False
