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

from heartbeat include HeartBeat

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

        heartbeat = HeartBeat(last_heartbeat)

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
        param['last_heartbeat'] = self.heartbeat.value
        return param

    def get_id(self):
        return self._node_id

    def get_name(self):
        return self._name

    def get_domain_name(self):
        return self._domain_name

    def get_port(self):
        return self._port

    def get_connection_url(self):
        return self.get_domain_name() + ':' + self.get_port()

    def is_valid(self):
        if (self.get_name() and
            self.get_domain_name() and
            self.get_port()):
            return True
        else:
            return False
