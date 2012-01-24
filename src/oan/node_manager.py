#!/usr/bin/env python
'''


'''

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import asyncore
import socket
import time
import os
import datetime
import uuid
from Queue import Queue

from oan import loop, database
from oan.util import log
from oan.heartbeat import OANHeartbeat
from oan.message import OANMessageNodeSync, OANMessageHeartbeat, OANMessageRelay, OANMessagePing
from oan.statistic import OANNetworkNodeStatistic
from oan.database import OANDatabase

class OANNetworkNodeState:
    connecting, connected, disconnected = range(1, 4)

"""
TODO
    All members should be private and we should use get/set which are thread safe.

    def get()
        return (sdf), sadf ,sadf, )

    def set(uuid, host, port, blocked)
        with self._lock:
            self.name = name

"""
class OANNetworkNode:
    uuid = None
    name = None
    port = None
    host = None
    state = None
    blocked = None # if server is listen or its blocked by router or firewall.

    heartbeat = None
    statistic = None

    out_queue = None

    def __init__(self, uuid):
        self.state = OANNetworkNodeState.disconnected
        self.heartbeat = OANHeartbeat()
        self.out_queue = Queue(10)
        self.uuid = uuid

    @classmethod
    def create(cls, uuid, host, port, blocked):
        obj = cls(uuid)
        obj.host, obj.port, obj.blocked = host, port, blocked
        obj.statistic = OANNetworkNodeStatistic()
        return obj

    def unserialize(self, data):
        self.host, self.port, self.blocked, subdata = data
        self.statistic = OANNetworkNodeStatistic()
        self.statistic.unserialize(subdata)

    def serialize(self):
        return(self.host, self.port, self.blocked, self.statistic.serialize())

    def __str__(self):
        return 'OANNetworkNode(%s, %s, %s) (queue: %s) (%s) (%s)' % (
            self.uuid, self.host, self.port,
            self.out_queue.qsize(),
            self.heartbeat.time, self.statistic
        )

class OANNodeManager():
    # Node server to connect and send message to other node servers
    config = None
    server = None

    # A dictionary with all nodes in the OAN.
    _nodes = {}

    # Info about my own node.
    _my_node = None

    def __init__(self, config):
        self.config = config

    # load all nodes in to memory, later on load only the best 1000 nodes.
    def load(self):
        for node in database().select_all(OANNetworkNode):
            log.info(node)
            self._nodes[node.uuid] = node

        if uuid.UUID(self.config.node_uuid) in self._nodes:
            my_node = self._nodes[uuid.UUID(self.config.node_uuid)]
            my_node.host  = self.config.node_domain_name
            my_node.port = int(self.config.node_port)
            my_node.blocked = self.config.blocked

            log.info(my_node)
        else:
            my_node = self.create_node(
                uuid.UUID(self.config.node_uuid),
                self.config.node_domain_name,
                self.config.node_port,
                self.config.blocked
            )

        self.add_node(my_node)
        self.set_my_node(my_node)

    # store all nodes in to database
    def store(self):
        database().replace_all(self._nodes.values())

    def dump(self):
        log.info("------ dump begin ------")
        for n in self._nodes.values():
            log.info("\t %s" % n)
        log.info("------ dump end ------")

    def create_node(self, uuid, host, port, blocked):
        #if not isinstance(uuid, UUID):
         #    print "OANNodeManager:Error uuid must be UUID instance"

        if self.exist_node(uuid):
            node = self._nodes[uuid]
            node.host = host
            node.port = int(port)
            node.blocked = blocked
        else:
            node = OANNetworkNode.create(uuid, host, int(port), blocked)
            self._nodes[uuid] = node

        return node

    def set_my_node(self, node):
        if self._my_node is None:
            self._my_node = node
        else:
            log.info("OANNodeManager:Error my node is already set")

    def get_my_node(self):
        #with self._lock:
        return self._my_node

    def get_statistic(self):
        return self._my_node.statistic

    def add_node(self, node):
        self._nodes[node.uuid] = node
        return node

    def exist_node(self, uuid):
        return (uuid in self._nodes)

    def get_node(self, uuid):
        return self._nodes[uuid]

    #TODO: remove dead nodes in database
    def remove_dead_nodes(self):
        for n in self._nodes.values():
            if n.uuid != self._my_node.uuid:
                if n.heartbeat.is_dead():
                    del self._nodes[n.uuid]

    #TODO: maybe should send heartbeat to blocked nodes to test. once a week or so.
    def send_heartbeat(self):
        heartbeat = OANMessageHeartbeat.create(self._my_node)
        for n in self._nodes.values():
            if n.uuid != self._my_node.uuid and not n.blocked:
                if n.heartbeat.is_expired():
                    self.send(n.uuid, heartbeat)

    #TODO sync ony with open nodes
    def send_node_sync(self):
        node_sync = OANMessageNodeSync.create()
        for n in self._nodes.values():
            if n.uuid != self._my_node.uuid:
                self.send(n.uuid, node_sync)

    #TODO: not all message should be relay
    def send(self, uuid, message):
        if (uuid in self._nodes):
            node = self._nodes[uuid]
            if node.blocked and self._my_node.blocked:
                self.relay(uuid, message)
            else:

                try:
                    node.out_queue.put(message, False)
                    self._my_node.statistic.out_queue_inc()
                except:
                    log.info("Queue full cleaning up")
                    save_messages = []
                    while True:
                        try:
                            message_on_queue = node.out_queue.get(False)
                            if message_on_queue.ttl:
                                save_message.append(message_on_queue)
                            else:
                                log.info("remove %s" % message_on_queue)
                        except:
                            log.info("empty cleaning up")
                            break

                    #TODO check if all save_messages culd be put back on queue.
                    for m in save_messages:
                        node.out_queue.put(m)

                    node.out_queue.put(message)

                if node.state == OANNetworkNodeState.disconnected:
                    loop().connect_to_node(node)
        else:
            log.info("OANNodeManager:Error node is missing %s" % uuid)
            log.info(self._nodes)


    #TODO: find good relay nodes.
    def relay(self, destination_uuid, message):
        relay = OANMessageRelay.create(self._my_node.uuid, destination_uuid, message)
        for relay_node in self._nodes.values():
            if relay_node.uuid != self._my_node.uuid:
                if not relay_node.blocked:
                    log.info("Relay %s to [%s] throw [%s]" % (message.__class__.__name__, destination_uuid, relay_node.uuid))
                    self.send(relay_node.uuid, relay)
                    return

        log.info("OANNodeManager:Error can not relay message no relay node found")

    def shutdown(self):
        pass


