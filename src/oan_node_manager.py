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
import thread
import oan
import uuid

from threading import Thread
from threading import Timer
from Queue import Queue

from oan_heartbeat import OANHeartbeat
from oan_message import OANMessageDispatcher, OANMessageNodeSync, OANMessageHeartbeat, OANMessageRelay, OANMessagePing
from oan_statistic import OANNetworkNodeStatistic
from oan_database import OANDatabase

class OANNetworkNodeState:
    connecting, connected, disconnected = range(1, 4)

class OANNetworkNode:
    heartbeat = None
    uuid = None
    name = None
    port = None
    host = None
    state = None
    blocked = None # if server is listen or its blocked by router or firewall.
    statistic = None

    out_queue = None

    def __init__(self, uuid):
        self.state = OANNetworkNodeState.disconnected
        self.heartbeat = OANHeartbeat()
        self.out_queue = Queue()
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
        self.unserialize(subdata)

    def serialize(self):
        return(self.host, self.port, self.blocked, statistic.serialize())

    def __str__(self):
        return 'OANNetworkNode(%s, %s, %s)' % (self.uuid, self.host, self.port)

class OANNodeManager():
    # Node server to connect and send message to other node servers
    server = None
    in_queue = None

    # A dictionary with all nodes in the OAN.
    _nodes = {}

    # Info about my own node.
    _my_node = None

    def __init__(self):
        self.in_queue = Queue()

    # load all nodes in to memory, later on load only the best 1000 nodes.
    def load(self, database):
        for node in database.select_all(OANNetworkNode):
            self._nodes[node.uuid] = node

        print self._nodes;

    # store all nodes in to database
    def store(self, database):
        database.replace_all(self._nodes.values())
        print "stored nodes in database"

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

        node.heartbeat.touch()
        return node

    def set_my_node(self, node):
        if self._my_node is None:
            from oan_server import OANServer
            self.server = OANServer()
            if not node.blocked:
                self.server.start_listen(node)

            self._my_node = node
        else:
            print "OANNodeManager:Error my node is already set"

    def get_my_node(self):
        return self._my_node

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
            if n.heartbeat.is_dead():
                del _nodes[n.uuid]

    def send_heartbeat(self):
        heartbeat = OANMessageHeartbeat.create(self._my_node)
        for n in self._nodes.values():
            if n.uuid != heartbeat.uuid:
                if n.heartbeat.is_expired():
                    self.send(n.uuid, heartbeat)

    def send_node_sync(self):
        node_sync = OANMessageNodeSync.create()
        for n in self._nodes.values():
            if n.uuid != node_sync.node_uuid:
                self.send(n.uuid, node_sync)

    #TODO: not all message should be relay
    def send(self, uuid, message):

        if (uuid in self._nodes):
            node = self._nodes[uuid]
            if node.blocked and self._my_node.blocked:
                self.relay(uuid, message)
            else:
                node.out_queue.put(message)

                if node.state == OANNetworkNodeState.disconnected:
                    self.server.connect_to_node(node)
        else:
            print "OANNodeManager:Error node is missing %s" % uuid
            print self._nodes


    #TODO: find good relay nodes.
    def relay(self, destination_uuid, message):
        relay = OANMessageRelay.create(self._my_node.uuid, destination_uuid, message)
        for relay_node in self._nodes.values():
            if relay_node.uuid != self._my_node.uuid:
                if not relay_node.blocked:
                    print "Relay %s to [%s] throw [%s]" % (message.__class__.__name__, destination_uuid, relay_node.uuid)
                    self.send(relay_node.uuid, relay)
                    return

        print "OANNodeManager:Error can not relay message no relay node found"

    # maybe choose from nodelist if bff fails. just use bff if nodes list is empty.
    # our test network just know bff so if 2 fails from start there will be 2 seperate networks, for now wait for bff
    # TODO: increase sleep time after every failed.
    def connect_to_oan(self, host, port):
        found = False
        while not found:
            self.server.connect_to_oan(host, port)

            # check if there are connected nodes that are not blocked in bridges
            for bridges in self.server.bridges.values():
                if bridges.node.host == host and bridges.node.port == port:
                    found = True

            time.sleep(5)

        print "OANNodeManager: connected to bff"

    def shutdown(self):
        self.server.shutdown()
        self.dispatcher.stop()
        self.store()


