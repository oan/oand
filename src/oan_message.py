#!/usr/bin/env python
'''


'''

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import oan_serializer

class OANMessageHandshake():
    node_id = None
    host = None
    port = None

    @classmethod
    def create(cls, node_id, host, port):
        obj = cls()
        obj.node_id = node_id
        obj.host = host
        obj.port = port
        return obj

    def execute(self):
        print "%s %s %s" % (self.node_id, self.host, self.port)

        #verifiera avsandare
        #satt ready to transmitt
        pass

#######

from datetime import datetime

class OANMessagePing():
    node_id = None
    time = None

    @classmethod
    def create(cls, node_id):
        obj = cls()
        obj.node_id = node_id
        obj.time = str(datetime.now())

        return obj

    def execute(self):
        print "%s %s %s" % (self.node_id, self.host, self.port)
        print "(clock [%s] from [%s]" % (self.time, self.node_id)


oan_serializer.add("OANMessageHandshake", OANMessageHandshake)
oan_serializer.add("OANMessagePing", OANMessagePing)
