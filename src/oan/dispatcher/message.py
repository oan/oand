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

from oan import node_mgr

class OANMessageStaticGetNodeInfo:
    @staticmethod
    def execute():
        node = node_mgr().get_my_node()
        yield (
            node.heartbeat.value,
            node.uuid,
            node.name,
            node.port,
            node.host,
            node.state,
            node.blocked
        )
