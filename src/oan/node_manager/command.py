#!/usr/bin/env python
"""
Commands for node manager

A command are created on node 1 and executed on node1.

"""

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from oan.dispatcher.message import OANMessageHeartbeat, OANMessageNodeSync
from oan.manager import node_manager
from oan.heartbeat import OANHeartbeat
from oan.util import log

class OANCommandStaticStoreNodes():
    @staticmethod
    def execute():
        log.info("OANMessageStaticStoreNodes:execute")
        node_manager().store()


class OANCommandStaticLoadNodes():
    @staticmethod
    def execute():
        log.info("OANMessageStaticLoadNodes:execute")
        node_manager().load()


class OANCommandStaticHeartbeat():
    @staticmethod
    def execute():
        log.info("OANMessageStaticHeartbeat:execute")

        my_node = node_manager().get_my_node()

        # if my node is blocked send heartbeat to NOT_DEAD nodes, this will
        # open a connection and retrieve messages to me.
        nodes = []
        if my_node.is_blocked():
            nodes = node_manager().get_nodes(OANHeartbeat.NOT_DEAD)
        else:
            nodes = node_manager().get_nodes(OANHeartbeat.EXPIRED)

        heartbeat = OANMessageHeartbeat.create()
        for n in nodes:
            if not n.is_blocked() and not n.has_heartbeat_state(OANHeartbeat.DEAD):
                node_manager().send(n.oan_id, heartbeat)


class OANCommandCleanOutQueue():
    node = None

    @classmethod
    def create(cls, node):
        obj = cls()
        obj.node = node
        return obj

    def execute(self):
        log.info("OANCommandCleanOutQueue:execute")

        save_messages = []
        while True:
            try:
                message_on_queue = self.node.out_queue.get(False)
                if message_on_queue.ttl:
                    save_messages.append(message_on_queue)
                else:
                    log.info("Remove %s from queue" % message_on_queue)
            except:
                break

        for m in save_messages:
            log.info("Put back %s on queue" % m)
            self.node.out_queue.put(m)


class OANCommandStaticSyncNodes():
    @staticmethod
    def execute():
        log.info("OANMessageStaticSyncNodes:execute")
        node_sync = OANMessageNodeSync.create()
        for n in node_manager().get_nodes(OANHeartbeat.NOT_OFFLINE):
            node_manager().send(n.oan_id, node_sync)
