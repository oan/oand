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
from oan.async import serializer
from oan.util import log
from oan.heartbeat import OANHeartbeat

class OANMessageHandshake():
    oan_id = None
    host = None
    port = None
    blocked = None
    ttl = False

    @classmethod
    def create(cls):
        my_node = node_manager().get_my_node()

        obj = cls()
        obj.oan_id = str(my_node.oan_id)
        (name, obj.host, obj.port, obj.blocked, state, heartbeat) = my_node.get()

        log.info("OANMessageHandshake create: %s %s:%s blocked: %s" % (
            obj.oan_id, obj.host, obj.port, obj.blocked))

        return obj

    def execute(self):
        log.info(
            "OANMessageHandshake received: %s %s:%s blocked: %s" %
            (self.oan_id, self.host, self.port, self.blocked)
        )

        node = node_manager().create_node(
            UUID(self.oan_id), self.host, self.port, self.blocked
        )
        node.touch()

        #??return node


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
        node_manager().send(
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
    def create(cls):
        obj = cls()
        node = node_manager().get_my_node()
        obj.oan_id = str(node.oan_id)
        (
            dummy,
            obj.host,
            obj.port,
            dummy,
            dummy,
            dummy
        ) = node.get()
        return obj

    def execute(self):
        log.info("OANMessageHeartbeat: %s %s %s" % (self.oan_id, self.host, self.port))

#####

# Remove expired nodes, sync with lastest info. maybe need to create this
# message in node_manager thread. or copy the nodes dict before calling this
# function.

class OANMessageNodeListHash():
    oan_id = None
    nodes_hash = None
    ttl = False

    @classmethod
    def create(cls):
        obj = cls()
        obj.oan_id = str(node_manager().get_my_node().oan_id)
        obj.nodes_hash = node_manager().get_nodes_hash(OANHeartbeat.NOT_OFFLINE)
        return obj

    def execute(self):
        my_nodes_hash = node_manager().get_nodes_hash(OANHeartbeat.NOT_OFFLINE)

        print "%s != %s" % (self.nodes_hash, my_nodes_hash)
        if self.nodes_hash != my_nodes_hash:
            node_manager().send(
                UUID(self.oan_id),
                OANMessageNodeList.create()
            )


class OANMessageNodeList():
    oan_id = None
    nodes_list = None
    ttl = False

    @classmethod
    def create(cls):
        obj = cls()
        obj.oan_id = str(node_manager().get_my_node().oan_id)
        obj.nodes_list = node_manager().get_nodes_list(OANHeartbeat.NOT_OFFLINE)
        return obj

    def execute(self):
        for oan_id, host, port, blocked, heartbeat in self.nodes_list:
            current_node = node_manager().get_node(UUID(oan_id))

            if (
                    current_node is None or
                    current_node.has_older_heartbeat(OANHeartbeat(heartbeat))
                ):

                newnode = node_manager().create_node(
                    UUID(oan_id), str(host), port, blocked
                )
                newnode.update(heartbeat = heartbeat)

# Messages that will be possible to send to a remote node.

serializer.add(OANMessageHandshake)
serializer.add(OANMessageHeartbeat)
serializer.add(OANMessageNodeList)
serializer.add(OANMessageNodeListHash)
serializer.add(OANMessageRelay)
serializer.add(OANMessagePing)
