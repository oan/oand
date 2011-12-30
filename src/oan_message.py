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
from oan import node_manager

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
    blocked = None

    @classmethod
    def create(cls, uuid, host, port, blocked):
        obj = cls()
        obj.uuid = uuid
        obj.host = host
        obj.port = port
        obj.blocked = blocked
        return obj

    def execute(self):
        print "OANMessageHandshake: %s %s %s blocked:%s" % (self.uuid, self.host, self.port, self.blocked)


class OANMessageClose():
    uuid = None

    @classmethod
    def create(cls, uuid):
        obj = cls()
        obj.uuid = uuid
        return obj

    def execute(self):
        print "OANMessageClose: %s" % (self.uuid)

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

#####

# remove expired nodes, sync with lastest info.
# maybe need to create this message in node_manager thread. or copy the nodes dict before calling this
# function.

class OANMessageNodeSync():
    node_uuid = None
    node_list = None
    node_list_hash = None
    step = None

    @classmethod
    def create(cls, step = 1, l = None):
        obj = cls()
        obj.step = step
        obj.node_list = []
        obj.node_uuid = node_manager().get_my_node().uuid

        if l is None:
            l = obj.create_list()

        print "----- My List"
        print l[0]
        print l[1]
        print "----------------------"

        if step == 1:
            obj.node_list_hash = l[0]
            obj.node_list = None
        elif step == 2:
            obj.node_list_hash = l[0]
            obj.node_list = l[1]

        return obj

    def create_list(self):
        valuelist = []
        hashlist = []
        for node in node_manager()._nodes.values():
            valuelist.append((node.uuid, node.host, node.port))

        valuelist.sort()

        for value in valuelist:
            hashlist.append(hash(value))

        return (hash(tuple(hashlist)), valuelist)

    def create_hash(self):
        return

    def execute(self):
        print "----- List from %s " % self.node_uuid
        print self.node_list_hash
        print self.node_list
        print "----------------------"

        if self.step == 1:
            my_l = self.create_list()

            # if hash is diffrent continue to step 2, send over the list.
            if self.node_list_hash != my_l[0]:
                node_manager().send(
                    self.node_uuid,
                    OANMessageNodeSync.create(2, my_l)
                )

        if self.step == 2:
            for n in self.node_list:
                node_manager().create_node(n[0], n[1], n[2])

#######

from datetime import datetime

class OANMessagePing():
    node_uuid = None
    ping_id = None
    ping_begin_time = None
    ping_end_time = None
    ping_counter = None

    @classmethod
    def create(cls, ping_id, ping_counter = 1, ping_begin_time = None):
        obj = cls()
        obj.node_uuid = node_manager().get_my_node().uuid
        obj.ping_id = ping_id
        obj.ping_counter = ping_counter
        obj.ping_begin_time = ping_begin_time
        obj.ping_end_time = str(datetime.now())

        if obj.ping_begin_time is None:
            obj.ping_begin_time = obj.ping_end_time

        return obj

    def execute(self):
        if self.ping_counter == 1:
            print "Ping [%s][%d] from [%s] %s - %s" % (
                self.ping_id,
                self.ping_counter,
                self.node_uuid,
                self.ping_begin_time,
                self.ping_end_time
            )

        if self.ping_counter > 1:
            node_manager().send(
                self.node_uuid,
                OANMessagePing.create(self.ping_id, self.ping_counter-1, self.ping_begin_time)
            )

oan_serializer.add("OANMessageHandshake", OANMessageHandshake)
oan_serializer.add("OANMessageClose", OANMessageClose)
oan_serializer.add("OANMessageHeartbeat", OANMessageHeartbeat)
oan_serializer.add("OANMessageNodeSync", OANMessageNodeSync)
oan_serializer.add("OANMessagePing", OANMessagePing)
