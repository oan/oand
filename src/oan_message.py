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
import uuid
import oan
import threading


#####
from threading import Thread
from Queue import Queue
from oan_event import OANEvent
from oan import node_manager
from oan_database import OANDatabase



# TODO: OANMessageDispatcher should start more than one thread (consumer...)
class OANMessageDispatcher(Thread):

    config = None

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

    statistic = None  # statistic for my node

    # wait for the thread to start and stop
    _started = None

    def __init__(self, config):
        Thread.__init__(self)
        self.config = config
        self.queue = Queue()
        self._started = threading.Event()
        self.on_shutdown = OANEvent()
        self.on_message = OANEvent()

    def process(self, message):
        self.queue.put(message)
        self.statistic.in_queue_inc()

    def start(self):
        Thread.start(self)
        #wait for set in run
        self._started.wait()

    def stop(self):
        self.queue.put(None)
        #wait for clear in run
        self._started.wait()

    def run(self):
        print "OANMessageDispatcher: started"
        self.statistic = node_manager().get_statistic()
        self._started.set()
        while(True):
            message = self.queue.get()
            if message is None:
                break

            message.execute(self)
            self.statistic.in_queue_dec()
            self.on_message(message)

        print "OANMessageDispatcher: shutdown"
        self.on_shutdown()
        self._started.clear()

# TODO: maybe have a time_to_live datetime. if node vill be offline och dead etc. clear all queues.
class OANMessageHandshake():
    ttl = False
    uuid = None
    host = None
    port = None
    blocked = None

    @classmethod
    def create(cls, uuid, host, port, blocked):
        obj = cls()
        obj.uuid = str(uuid)
        obj.host = host
        obj.port = port
        obj.blocked = blocked
        return obj

    def execute(self, dispatcher):
        print "OANMessageHandshake: %s %s %s blocked:%s" % (self.uuid, self.host, self.port, self.blocked)


class OANMessageClose():
    uuid = None
    ttl = False

    @classmethod
    def create(cls, uuid):
        obj = cls()
        obj.uuid = str(uuid)
        return obj

    def execute(self, dispatcher):
        print "OANMessageClose: %s" % (self.uuid)

class OANMessageRelay():
    uuid = None
    destination_uuid = None
    message = None
    ttl = False


    @classmethod
    def create(cls, uuid, destination_uuid, message):
        obj = cls()
        obj.uuid = str(uuid)
        obj.destination_uuid = str(destination_uuid)
        obj.message = message
        return obj

    def execute(self, dispatcher):
        print "OANMessageRelay: %s %s" % (self.destination_uuid, self.message)
        node_manager().send(
            uuid.UUID(self.destination_uuid),
            self.message
        )


class OANMessageHeartbeat():
    '''


    The heartbeat touch will be done in bridge read and write.

    '''
    uuid = None
    host = None
    port = None
    ttl = False

    @classmethod
    def create(cls, node):
        obj = cls()
        obj.uuid = str(node.uuid)
        obj.host = node.host
        obj.port = node.port
        return obj

    def execute(self, dispatcher):
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
    ttl = False

    @classmethod
    def create(cls, step = 1, l = None):
        obj = cls()
        obj.step = step
        obj.node_list = []
        obj.node_uuid = str(node_manager().get_my_node().uuid)

        if l is None:
            l = obj.create_list()

        #print "----- My List"
        #print l[0]
        #print l[1]
        #print "----------------------"

        if step == 1:
            obj.node_list_hash = l[0]
            obj.node_list = None
        elif step == 2:
            obj.node_list_hash = l[0]
            obj.node_list = l[1]

        return obj

    # add heartbeat should not be included in hash
    def create_list(self):
        valuelist = []
        hashlist = []
        for node in node_manager()._nodes.values():
            valuelist.append((str(node.uuid), node.host, node.port, node.blocked, node.heartbeat.value))

        valuelist.sort()

        for value in valuelist:
            hashlist.append(hash(value))

        return (hash(tuple(hashlist)), valuelist)

    def create_hash(self):
        return

    def execute(self, dispatcher):
        #print "----- List from %s " % self.node_uuid
        #print self.node_list_hash
        #print self.node_list
        #print "----------------------"

        if self.step == 1:
            my_l = self.create_list()

            # if hash is diffrent continue to step 2, send over the list.
            if self.node_list_hash != my_l[0]:
                node_manager().send(
                    uuid.UUID(self.node_uuid),
                    OANMessageNodeSync.create(2, my_l)
                )

        if self.step == 2:
            for n in self.node_list:
                currentnode = node_manager().get_node(uuid.UUID(n[0]))
                if currentnode.heartbeat < n[4]:
                    newnode = node_manager().create_node(uuid.UUID(n[0]), n[1], n[2], n[3])
                    newnode.heartbeat.value = n[4]

#######

from datetime import datetime

class OANMessagePing():
    node_uuid = None
    ping_id = None
    ping_begin_time = None
    ping_end_time = None
    ping_counter = None
    ttl = False # Time to live TODO: should be a datetime

    @classmethod
    def create(cls, ping_id, ping_counter = 1, ping_begin_time = None):
        obj = cls()
        obj.node_uuid = str(node_manager().get_my_node().uuid)
        obj.ping_id = ping_id
        obj.ping_counter = ping_counter
        obj.ping_begin_time = ping_begin_time
        obj.ping_end_time = str(datetime.now())

        if obj.ping_begin_time is None:
            obj.ping_begin_time = obj.ping_end_time

        return obj

    def execute(self, dispatcher):
        #if self.ping_counter == 1:
        print "Ping [%s][%d] from [%s] %s - %s" % (
            self.ping_id,
            self.ping_counter,
            self.node_uuid,
            self.ping_begin_time,
            self.ping_end_time
        )

        if self.ping_counter > 1:
            node_manager().send(
                uuid.UUID(self.node_uuid),
                OANMessagePing.create(self.ping_id, self.ping_counter-1, self.ping_begin_time)
            )


### OANMessageStoreNodes can not be send over network
class OANMessageStoreNodes():
    ttl = True

    @classmethod
    def create(cls):
        obj = cls()
        return obj

    def execute(self, dispatcher):
        print "OANMessageStoreNodes"
        node_manager().store()


### OANMessageLoadNodes can not be send over network
class OANMessageLoadNodes():
    ttl = True

    @classmethod
    def create(cls):
        obj = cls()
        return obj

    def execute(self, dispatcher):
        print "OANMessageLoadNodes"
        node_manager().load()


oan_serializer.add("OANMessageHandshake", OANMessageHandshake)
oan_serializer.add("OANMessageClose", OANMessageClose)
oan_serializer.add("OANMessageHeartbeat", OANMessageHeartbeat)
oan_serializer.add("OANMessageNodeSync", OANMessageNodeSync)
oan_serializer.add("OANMessageRelay", OANMessageRelay)
oan_serializer.add("OANMessagePing", OANMessagePing)
