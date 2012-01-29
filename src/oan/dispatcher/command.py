#!/usr/bin/env python
"""
Messages that are sent to the "local" dispatcher.

"""

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from uuid import UUID

from oan import node_mgr, dispatch
from oan.network import serializer
from oan.util import log

class OANCommandShutdown:
    def execute(self):
        pass

class OANCommandStaticStoreNodes():

    @staticmethod
    def execute(dispatcher):
        log.info("OANMessageStaticStoreNodes")
        node_mgr().store()

class OANCommandStaticLoadNodes():

    @staticmethod
    def execute(dispatcher):
        log.info("OANMessageStaticLoadNodes")
        node_mgr().load()


class OANCommandStaticHeartbeat():

    @staticmethod
    def execute(dispatcher):
        log.info("OANMessageStaticHeartbeat")
        node_mgr().send_heartbeat()


class OANCommandStaticSyncNodes():

    @staticmethod
    def execute(dispatcher):
        log.info("OANMessageStaticSyncNodes")
        node_mgr().send_node_sync()


class OANCommandStaticGetNodeInfo:
    @staticmethod
    def execute(dispatcher):
        node = node_mgr().get_my_node()
        yield (
            node.heartbeat.value,
            node.oan_id,
            node.name,
            node.port,
            node.host,
            node.state,
            node.blocked
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


    def execute(self, dispatcher):
        node_manager = dispatcher.node_manager

        #log.debug("oan_id: %s, message: %s" % (self.oan_id, str(self.message)))
        node_manager.send(self.oan_id, self.message)




