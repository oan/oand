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

from oan_heartbeat import OANHeartbeat

class OANNetworkNode():
    heartbeat = None

    uuid = None
    name = None
    domain_name = None
    port = None

    def __init__(self, uuid, name, domain_name, port, last_heartbeat = "2006-06-06T06:06:06Z"):
        self.uuid = uuid
        self.name = name
        self.domain_name = domain_name
        self.port = port

        self.heartbeat = OANHeartbeat(last_heartbeat)

    @classmethod
    def create_from_dict(cls, args):
        return cls (
            args['uuid'],
            args['name'],
            args['domain_name'],
            args['port'],
            args['last_heartbeat']
        )

    def get_dict(self):
        param = {}
        param['uuid'] = self.uuid
        param['name'] = self.name
        param['domain_name'] = self.domain_name
        param['port'] = self.port
        param['last_heartbeat'] = self.heartbeat.value
        return param

    @property
    def connection_url(self):
        return "%s:%s" % (self.domain_name, self.port)

    def is_valid(self):
        if (self.uuid and self.name and self.domain_name and self.port):
            return True
        else:
            return False
