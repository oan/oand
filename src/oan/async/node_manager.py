#!/usr/bin/env python
"""
"""
__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

#from oan.manager import database
from oan.util import log
from oan.async.network_node import OANNetworkNode
from oan.async.bridge import OANBridgeAuth
from oan.util.network import get_local_host

class OANNodeManager():
    _config = None

    # A dictionary with all nodes in the OAN.
    _nodes = {}

    # Info about my own node.
    _my_node = None

    @staticmethod
    def init(config):
        OANNodeManager._config = config
        # OANNodeManager._auth = OANBridgeAuth.create(
        #     version = "oand v1.0",
        #     oan_id = config.oan_id,
        #     host = get_local_host(),
        #     port = config.node_port,
        #     blocked = config.blocked)

    @staticmethod
    def load():
        """ Load all nodes in to memory and set _my_node"""
        #for node in database().select_all(OANNetworkNode):
        #    OANNodeManager._add_node(node)

        if OANNodeManager._config.oan_id in OANNodeManager._nodes:
            OANNodeManager._set_my_node(OANNodeManager._nodes[OANNodeManager._config.oan_id])
        else:
            OANNodeManager._create_my_node()

    @staticmethod
    def store():
        #database().replace_all(OANNodeManager._nodes.values())
        pass

    @staticmethod
    def create_node(oan_id, host, port, blocked):
        return OANNodeManager._create_node(oan_id, host, port, blocked)

    @staticmethod
    def get_my_node():
        return OANNodeManager._my_node

    @staticmethod
    def get_auth():
        return OANNodeManager._auth

    @staticmethod
    def get_node(oan_id):
        if oan_id in OANNodeManager._nodes:
            return OANNodeManager._nodes[oan_id]

        return None

    @staticmethod
    def exist_node(oan_id):
        return oan_id in OANNodeManager._nodes

    @staticmethod
    def get_nodes(heartbeat_state = None):
        """
        Returns all nodes that have a specified heartbeat_state,
        """
        return OANNodeManager._get_nodes(heartbeat_state)

    @staticmethod
    def get_nodes_list(heartbeat_state = None):
        return OANNodeManager._get_nodes_list(heartbeat_state)

    @staticmethod
    def get_nodes_hash(heartbeat_state = None):
        hashlist = []

        for (oan_id, host, port, blocked, heartbeat) in OANNodeManager._get_nodes_list(heartbeat_state):
            hashlist.append( hash( (oan_id, host, port, blocked) ))

        return hash(tuple(hashlist))

    @staticmethod
    def send(oan_id, message):
        log.debug("oan_id: %s, message: %s" % (oan_id, str(message)))

        if (oan_id in OANNodeManager._nodes):
            node = OANNodeManager._nodes[oan_id]
            if node.is_blocked() and OANNodeManager._my_node.is_blocked():
                OANNodeManager._relay_to_node(oan_id, message)
            else:
                OANNodeManager._send_to_node(node, message)
        else:
            log.info("OANNodeManager:Error node is missing %s" % oan_id)
            log.info(OANNodeManager._nodes)

    @staticmethod
    def shutdown():
        return True

    @staticmethod
    def dump():
        print("------ dump begin ------")
        for n in OANNodeManager._nodes.values():
            print("%s" % n)
        print("------ dump end ------")


    @staticmethod
    def _create_node(oan_id, host, port, blocked):
        """
        create the node in the node dictionary. if the node already exists
        "host,port,blocked" will be updated.

        """

        if oan_id in OANNodeManager._nodes:
            node = OANNodeManager._nodes[oan_id]
            node.update(host = host, port = port,
                        blocked = blocked)
        else:
            node = OANNetworkNode.create(oan_id, host, port, blocked)
            OANNodeManager._nodes[oan_id] = node

        return node


    @staticmethod
    def _add_node(node):
        """
        add a node to the node dictionary. if the node already exists it
        updates the host, port, blocked.
        """
        if node.oan_id in OANNodeManager._nodes:
            n = OANNodeManager._nodes[node.oan_id]
            n.update(host = node.host, port = node.port,
                        blocked = node.blocked)
        else:
            OANNodeManager._nodes[node.oan_id] = node

    @staticmethod
    def _set_my_node(node):
        """
        set my node and update the host, port, blocked from the config.
        """
        if OANNodeManager._my_node is None:
            node.update(
                host = OANNodeManager._config.node_domain_name,
                port = int(OANNodeManager._config.node_port),
                blocked = OANNodeManager._config.blocked)

            OANNodeManager._my_node = node
            OANNodeManager._my_node.touch()
        else:
            log.info("OANNodeManager:Error my node is already set")

    @staticmethod
    def _create_my_node():
        """
        create a new node from config and set it to my node.
        """
        if OANNodeManager._my_node is None:
            node = OANNodeManager._create_node(
                OANNodeManager._config.oan_id,
                OANNodeManager._config.node_domain_name,
                int(OANNodeManager._config.node_port),
                OANNodeManager._config.blocked
            )

            OANNodeManager._my_node = node
            OANNodeManager._my_node.touch()
        else:
            log.info("OANNodeManager:Error my node is already set")

    @staticmethod
    def _get_nodes(heartbeat_state = None, include_my_node = False):
        """
        Returns all nodes that have a specified heartbeat_state,
        """

        ret = []
        for n in OANNodeManager._nodes.values():
            if (
                (include_my_node or n.oan_id != OANNodeManager._my_node.oan_id) and
                (heartbeat_state is None or n.has_heartbeat_state(heartbeat_state))):
                    ret.append(n)

        return ret

    @staticmethod
    def _get_nodes_list(heartbeat_state = None):
        valuelist = []
        for node in OANNodeManager._get_nodes(heartbeat_state, True):
            (
                name,
                host,
                port,
                blocked,
                state,
                heartbeat
            ) = node.get()

            oan_id = str(node.oan_id)
            valuelist.append((oan_id, host, port, blocked, heartbeat))

        valuelist.sort()
        return valuelist
