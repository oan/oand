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

#####
from threading import Thread
from Queue import Queue
from oan_event import OANEvent
class OANMessageDispatcher(Thread):

    ''' use: dispatcher.on_shutdown += my_loop_shutdown() '''
    on_shutdown = None

    '''
        use:

        def got_message(self, message):
            print "got message"

        dispatcher.on_message += [got_message]
    '''
    on_message = None

    queue = None

    def __init__(self):
        Thread.__init__(self)
        self.queue = Queue()
        self.on_shutdown = OANEvent()
        self.on_message = OANEvent()

    def start(self):
            Thread.start(self)

    def stop(self):
        self.queue.put(None)

    def run(self):
        print "OANMessageDispatcher: started"
        while(True):
            message = self.queue.get()
            if message is None:
                break

            message.execute()
            self.on_message(message)

        print "OANMessageDispatcher: shutdown"
        self.on_shutdown()

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
        print "OANMessageHandshake: %s %s %s" % (self.uuid, self.host, self.port)


# TODO: maybe have a time_to_live datetime. if node vill be offline och dead etc. clear all queues.
class OANMessageHeartbeat():
    uuid = None
    host = None
    port = None

    @classmethod
    def create(cls, node):
        obj = cls()
        obj.uuid = node.uuid
        obj.host = node.host
        obj.port = node.port
        return obj

    def execute(self):
        print "OANMessageHeartbeat: %s %s %s" % (self.uuid, self.host, self.port)



#######

from datetime import datetime

class OANMessagePing():
    uuid = None
    nr = None
    time = None

    @classmethod
    def create(cls, uuid, nr):
        obj = cls()
        obj.uuid = uuid
        obj.nr = nr
        obj.time = str(datetime.now())

        return obj

    def execute(self):
        if ((self.nr%1000) == 0):
            print "Ping [%d][%s] from [%s]" % (self.nr, self.time, self.uuid)


oan_serializer.add("OANMessageHandshake", OANMessageHandshake)
oan_serializer.add("OANMessageHeartbeat", OANMessageHeartbeat)
oan_serializer.add("OANMessagePing", OANMessagePing)
