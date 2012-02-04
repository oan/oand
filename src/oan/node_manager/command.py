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

from oan.dispatcher.message import OANMessageHeartbeat
from oan.manager import node_manager
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

        heartbeat = OANMessageHeartbeat.create(node_manager().get_my_node())
        for n in node_manager().get_nodes():
            if not n.blocked:
                node_manager().send(n.oan_id, heartbeat)


class OANCommandStaticSyncNodes():
    @staticmethod
    def execute():
        log.info("OANMessageStaticSyncNodes:execute")
        node_manager().send_node_sync()
