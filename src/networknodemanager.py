#!/usr/bin/env python
'''
Connection managment between nodes.

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import logging
import sys

from abc import ABCMeta, abstractmethod

from networknode import NetworkNode

class NetworkNodeManager():
    '''Abstract class for Networknodes'''
    __metaclass__ = ABCMeta

    _client_class = None
    _logger = None

    def __init__(self, client_class, logger):
        self._client_class = client_class
        self._logger = logger

#    @abstractmethod
#    def join_remote_server(self, remote_node):
#        pass

#    @abstractmethod
#    def add_node(self, name, domain_name, port):
#        pass

class CircularNetworkNodeManager(NetworkNodeManager):
    # Info about my own node.
    _my_node = None

    # An dictionary with all nodes in the OAN.
    _nodes = {}

    def set_my_node(self, node):
        self._my_node = node

    def get_my_node(self):
        return self._my_node

    def add_node(self, node):
        self._nodes[node.get_id()] = node
        self._remove_myself_from_nodes()

    def get_node(self, node_id):
        return self._nodes[node_id]

    def add_nodes(self, nodes):
        '''
        Merge nodes with internal nodes, replacing existing nodes.

        '''
        self._nodes.update(nodes)
        self._remove_myself_from_nodes()

    def get_nodes(self):
        return self._nodes

    def _remove_myself_from_nodes(self):
        if self.get_my_node().get_id() in self._nodes:
            del(self._nodes[self.get_my_node().get_id()])

    def connect_to_oan(self):
        if len(self._nodes):
            for node in self._nodes.itervalues():
                if (self.connect_to_node(node)):
                    return
            self._logger.warning("Failed to connect to all friends.")

    def check_heartbeat(self):
        for node_id, node in self._nodes.iteritems():
            if (node.heartbeat.is_inactive()):
                self.connect_to_node(node)
                # Connect to node will check heartbeat on all nodes.
                return
            elif (node.heartbeat.is_expired()):
                self.send_heartbeat(node)

    def connect_to_node(self, node):
        self._logger.debug("Connect to node: " + node.get_name())
        try:
            remote_node = self._client_class()
            remote_node.connect(node.get_connection_url())
            nodes = remote_node.get_nodes(self.get_my_node())
            self._logger.info("Add %d nodes from %s" % (
                              len(nodes),
                              node.get_connection_url()))
            self.add_nodes(nodes)

            # We just recived data from this node, so it's alive.
            self.touch_last_heartbeat(node)
            self.check_heartbeat()
            return True
        except IOError as (errno, strerror):
            self._logger.warning(
                "Failed to connect to: " + node.get_name() + " " +
                "(I/O error({0}): {1}".format(errno, strerror) + ')')
        except:
            self._logger.warning(
                "Failed to connect to: " + node.get_name() +
                "Unexpected error: " + str(sys.exc_info()))
        return False

    def send_heartbeat(self, node):
        self._logger.debug("Send heartbeat to: " + node.get_name())
        try:
            remote_node = self._client_class()
            remote_node.connect(node.get_connection_url())
            response = remote_node.send_heartbeat(self.get_my_node())
            if response['status'] == 'ok':
                self.touch_last_heartbeat(node)
                return True
        except:
            self._logger.warning(
                "Failed to connect to: " + node.get_name() +
                "Unexpected error: " + str(sys.exc_info()))

        return False

    def touch_last_heartbeat(self, node):
        if node.get_id() not in self._nodes:
            logging.getLogger('oand').debug(
                "Unknown node %s is touching me, adding to my nodes list." %
                vars(node))
            # When the heartbeat is expired, the next once-a-minute-scheduler
            # will ask the new node for it's node list.
            # The new node might know about nodes we are not aware of.
            node.heartbeat.set_expired()
            self.add_node(node)
        else:
            self._nodes[node.get_id()].heartbeat.touch()

    def remove_expired_nodes(self):
        nodes_to_remove = []
        for node_id, node in self._nodes.iteritems():
            if (node.heartbeat.is_dead()):
                nodes_to_remove.append(node_id)
        for node_id in nodes_to_remove:
            del(self._nodes[node_id])

    def get_dbg_nodes(self):
        nodes = self._my_node.get_name()
        for node in self.get_nodes().itervalues():
            nodes += " - "
            nodes += node.get_name()

        return nodes
