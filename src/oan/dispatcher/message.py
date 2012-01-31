#!/usr/bin/env python
"""
Messages that are sent to the "remote" dispatcher.

A message are created on node 1 and executed in the dispatcher of a remote
node.

"""

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from uuid import UUID
from datetime import datetime

from oan.manager import node_manager
from oan.network import serializer
from oan.util import log


class OANMessageHandshake():
    oan_id = None
    host = None
    port = None
    blocked = None
    ttl = False

    @classmethod
    def create(cls, oan_id, host, port, blocked):
        obj = cls()
        obj.oan_id = str(oan_id)
        obj.host = host
        obj.port = port
        obj.blocked = blocked
        return obj

    def execute(self):
        log.info(
            "OANMessageHandshake: %s %s:%s blocked: %s" %
            (self.oan_id, self.host, self.port, self.blocked)
        )
        yield node_manager().create_node(
            UUID(self.oan_id), self.host, self.port, self.blocked
        )


class OANMessageClose():
    oan_id = None
    ttl = False

    @classmethod
    def create(cls, oan_id):
        obj = cls()
        obj.oan_id = str(oan_id)
        return obj

    def execute(self):
        log.info("OANMessageClose: %s" % (self.oan_id))


class OANMessagePing:
    """
    Sending this message over the network will put the message in the remote
    dispatcher and "execute" method will be called. It creates a new
    ping and send it back to the origin node. The ping will bounce back
    and forward until ping_counter are zero.

    oan_id
        this nodes oan_id.

    ping_id
        just an id that can be used to identify a ping.

    ping_begin_time
        the first ping is created.

    ping_end_time
        the last ping is created.

    ping_counter
        number of times the ping will be sent over the network. To get a
        ping back from remote node set ping_counter to 2.

    """
    oan_id = None
    ping_id = None
    ping_begin_time = None
    ping_end_time = None
    ping_counter = None
    ttl = False

    @classmethod
    def create(cls, oan_id, ping_id, ping_counter = 2, ping_begin_time = None):
        """creates a ping message."""
        obj = cls()
        obj.oan_id = str(oan_id)
        obj.ping_id = ping_id
        obj.ping_counter = ping_counter
        obj.ping_begin_time = ping_begin_time
        obj.ping_end_time = str(datetime.now())

        if obj.ping_begin_time is None:
            obj.ping_begin_time = obj.ping_end_time

        return obj

    def execute(self):
        """A ping is received log it and send it back."""
        log.info("Ping [%s][%d] from [%s] %s - %s" % (
            self.ping_id,
            self.ping_counter,
            self.oan_id,
            self.ping_begin_time,
            self.ping_end_time
        ))

        if self.ping_counter > 1:
            node_manager().send(
                self.oan_id,
                OANMessagePing.create(node_manager().get_my_node().oan_id, self.ping_id, self.ping_counter-1, self.ping_begin_time)
            )


class OANMessageRelay():
    oan_id = None
    destination_oan_id = None
    message = None
    ttl = False

    @classmethod
    def create(cls, oan_id, destination_oan_id, message):
        obj = cls()
        obj.oan_id = str(oan_id)
        obj.destination_oan_id = str(destination_oan_id)
        obj.message = message
        return obj

    def execute(self):
        log.info("OANMessageRelay: %s %s" % (self.destination_oan_id, self.message))
        node_manager.send(
            UUID(self.destination_oan_id),
            self.message
        )


class OANMessageHeartbeat():
    """


    The heartbeat touch will be done in bridge read and write.

    """
    oan_id = None
    host = None
    port = None
    ttl = False

    @classmethod
    def create(cls, node):
        obj = cls()
        obj.oan_id = str(node.oan_id)
        obj.host = node.host
        obj.port = node.port
        return obj

    def execute(self):
        log.info("OANMessageHeartbeat: %s %s %s" % (self.oan_id, self.host, self.port))

#####

# Remove expired nodes, sync with lastest info. maybe need to create this
# message in node_manager thread. or copy the nodes dict before calling this
# function.

class OANMessageNodeSync():
    node_oan_id = None
    node_list = None
    node_list_hash = None
    step = None
    ttl = False

    @classmethod
    def create(cls, step = 1, l = None):
        obj = cls()
        obj.step = step
        obj.node_list = []
        obj.node_oan_id = str(node_manager().get_my_node().oan_id)

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

    def create_list(self):
        valuelist = []
        hashlist = []
        for node in node_manager()._nodes.values():
            valuelist.append((str(node.oan_id), node.host, node.port, node.blocked, node.heartbeat.value))

        valuelist.sort()

        for value in valuelist:
            hashlist.append( hash( (value[0], value[1], value[2], value[3]) ))

        return (hash(tuple(hashlist)), valuelist)

    def create_hash(self):
        return

    def execute(self):
        #print "----- List from %s " % self.node_oan_id
        #print self.node_list_hash
        #print self.node_list
        #print "----------------------"

        if self.step == 1:
            my_l = self.create_list()

            # if hash is diffrent continue to step 2, send over the list.
            if self.node_list_hash != my_l[0]:
                node_manager.send(
                    UUID(self.node_oan_id),
                    OANMessageNodeSync.create(2, my_l)
                )

        if self.step == 2:
            for n in self.node_list:
                currentnode = node_manager.get_node(UUID(n[0]))
                if currentnode.heartbeat < n[4]:
                    newnode = node_manager.create_node(UUID(n[0]), n[1], n[2], n[3])
                    newnode.heartbeat.value = n[4]


# Messages that will be possible to send to a remote node.

serializer.add("OANMessageHandshake", OANMessageHandshake)
serializer.add("OANMessageClose", OANMessageClose)
serializer.add("OANMessageHeartbeat", OANMessageHeartbeat)
serializer.add("OANMessageNodeSync", OANMessageNodeSync)
serializer.add("OANMessageRelay", OANMessageRelay)
serializer.add("OANMessagePing", OANMessagePing)
