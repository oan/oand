#!/usr/bin/env python
"""
Commands that are sent to the "local" dispatcher.

A command are created on node 1 and executed on node1.

"""

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from oan.manager import node_manager
from oan.util import log


class OANCommandShutdown:
    def execute(self):
        pass


class OANCommandStaticStoreNodes():
    @staticmethod
    def execute():
        log.info("OANMessageStaticStoreNodes")
        node_manager().store()


class OANCommandStaticLoadNodes():
    @staticmethod
    def execute():
        log.info("OANMessageStaticLoadNodes")
        node_manager().load()


class OANCommandStaticHeartbeat():
    @staticmethod
    def execute():
        log.info("OANMessageStaticHeartbeat")
        node_manager().send_heartbeat()


class OANCommandStaticSyncNodes():
    @staticmethod
    def execute():
        log.info("OANMessageStaticSyncNodes")
        node_manager().send_node_sync()


class OANCommandStaticGetNodeInfo:
    @staticmethod
    def execute():
        node = node_manager().get_my_node()
        if node == None:
            yield ("Invalid node")
        else:
            (
                name,
                host,
                port,
                blocked,
                state,
                heartbeat
            ) = node.get()

            yield (
                node.oan_id,
                name,
                host,
                port,
                blocked,
                state,
                heartbeat
            )


class OANCommandSendToNode:
    oan_id = None
    message = None

    @classmethod
    def create(cls, oan_id, message):
        obj = cls()
        obj.oan_id = oan_id
        obj.message = message
        return obj

    def execute(self, ):
        log.debug("oan_id: %s, message: %s" % (
            self.oan_id, str(self.message))
        )
        node_manager().send(self.oan_id, self.message)
