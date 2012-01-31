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
from uuid import UUID
from Queue import Queue

from oan.manager import network, database, dispatcher
from oan.util import log
from oan.heartbeat import OANHeartbeat
from oan.dispatcher.message import OANMessageNodeSync, OANMessageHeartbeat, OANMessageRelay, OANMessagePing
from oan.statistic import OANNetworkNodeStatistic
from oan.database import OANDatabase
from oan.network.network_node import OANNetworkNode
from oan.network.command import NetworksCommandConnectToNode

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
            self._nodes[node.oan_id] = node

        if UUID(self.config.node_uuid) in self._nodes:
            my_node = self._nodes[UUID(self.config.node_uuid)]
            my_node.host  = self.config.node_domain_name
            my_node.port = int(self.config.node_port)
            my_node.blocked = self.config.blocked

            log.info(my_node)
        else:
            my_node = self.create_node(
                UUID(self.config.node_uuid),
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

    def create_node(self, oan_id, host, port, blocked):
        #if not isinstance(oan_id, UUID):
         #    print "OANNodeManager:Error oan_id must be UUID instance"

        if self.exist_node(oan_id):
            node = self._nodes[oan_id]
            node.host = host
            node.port = int(port)
            node.blocked = blocked
        else:
            node = OANNetworkNode.create(oan_id, host, int(port), blocked)
            self._nodes[oan_id] = node

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
        self._nodes[node.oan_id] = node
        return node

    def exist_node(self, oan_id):
        return (oan_id in self._nodes)

    def get_node(self, oan_id):
        return self._nodes[oan_id]

    #TODO: remove dead nodes in database
    def remove_dead_nodes(self):
        for n in self._nodes.values():
            if n.oan_id != self._my_node.oan_id:
                if n.heartbeat.is_dead():
                    del self._nodes[n.oan_id]

    #TODO: maybe should send heartbeat to blocked nodes to test. once a week or so.
    def send_heartbeat(self):
        heartbeat = OANMessageHeartbeat.create(self._my_node)
        for n in self._nodes.values():
            if n.oan_id != self._my_node.oan_id and not n.blocked:
                if n.heartbeat.is_expired():
                    self.send(n.oan_id, heartbeat)

    #TODO sync ony with open nodes
    def send_node_sync(self):
        node_sync = OANMessageNodeSync.create()
        for n in self._nodes.values():
            if n.oan_id != self._my_node.oan_id:
                self.send(n.oan_id, node_sync)

    #TODO: not all message should be relay
    def send(self, oan_id, message):
        log.debug("oan_id: %s, message: %s" % (oan_id, str(message)))

        if (oan_id in self._nodes):
            node = self._nodes[oan_id]
            if node.blocked and self._my_node.blocked:
                self.relay(oan_id, message)
            else:

                #try:
                node.out_queue.put(message, False)
                #    self._my_node.statistic.out_queue_inc()
                #except:
                #    log.info("Queue full cleaning up")
                #    save_messages = []
                #    while True:
                #        try:
                #            message_on_queue = node.out_queue.get(False)
                #            if message_on_queue.ttl:
                #                save_message.append(message_on_queue)
                #            else:
                #                log.info("remove %s" % message_on_queue)
                #        except:
                #            log.info("empty cleaning up")
                #            break

                    #TODO check if all save_messages culd be put back on queue.
                 #   for m in save_messages:
                 #       node.out_queue.put(m)

                  #  node.out_queue.put(message)

                if node.is_disconnected():
                    network().execute(NetworksCommandConnectToNode.create(node))
        else:
            log.info("OANNodeManager:Error node is missing %s" % oan_id)
            log.info(self._nodes)


    #TODO: find good relay nodes.
    def relay(self, destination_uuid, message):
        relay = OANMessageRelay.create(self._my_node.oan_id, destination_uuid, message)
        for relay_node in self._nodes.values():
            if relay_node.oan_id != self._my_node.oan_id:
                if not relay_node.blocked:
                    log.info("Relay %s to [%s] throw [%s]" % (message.__class__.__name__, destination_uuid, relay_node.oan_id))
                    self.send(relay_node.oan_id, relay)
                    return

        log.info("OANNodeManager:Error can not relay message no relay node found")

    def shutdown(self):
        pass


