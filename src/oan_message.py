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


# TODO: maybe have a time_to_live datetime. if node vill be offline och dead etc. clear all queues.
class OANMessageHandshake():
    uuid = None
    host = None
    port = None

    @classmethod
    def create(cls, uuid, host, port):
        obj = cls()
        obj.uuid = uuid
        obj.host = host
        obj.port = port
        return obj

    def execute(self):
        print "%s %s %s" % (self.uuid, self.host, self.port)

        #verifiera avsandare
        #satt ready to transmitt
        pass

#######

from datetime import datetime

class OANMessagePing():
    uuid = None
    time = None

    @classmethod
    def create(cls, uuid):
        obj = cls()
        obj.uuid = uuid
        obj.time = str(datetime.now())

        return obj

    def execute(self):
        print "%s %s %s" % (self.uuid, self.host, self.port)
        print "(clock [%s] from [%s]" % (self.time, self.uuid)


oan_serializer.add("OANMessageHandshake", OANMessageHandshake)
oan_serializer.add("OANMessagePing", OANMessagePing)
