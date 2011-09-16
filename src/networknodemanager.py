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

    def add_node(self, node):
        self._nodes[node.get_id()] = node

    def get_node(self, node_id):
        return self._nodes[node_id]

    def set_my_node(self, node):
        self._my_node = node

    def get_my_node(self):
        return self._my_node

    def merge_nodes(self, nodes):
        '''
        Merge nodes with internal nodes, replacing existing nodes.

        '''
        self._logger.info("Merging node list")
        self._nodes.update(nodes)

    def get_nodes(self):
        return self._nodes

    def connect_to_oan(self):
        if len(self._nodes):
            remote_node = self._client_class(self._my_node.get_name())
            for node in self._nodes.itervalues():
                try:
                    remote_node.connect(node.get_connection_url())
                    nodes = remote_node.get_nodes()
                    self.merge_nodes(nodes)
                    return
                except IOError as (errno, strerror):
                    self._logger.warning(
                        "Failed to connect to: " + node.get_name() + " " +
                        "(I/O error({0}): {1}".format(errno, strerror) + ')')
                except:
                    self._logger.warning(
                        "Failed to connect to: " + node.get_name() +
                        "Unexpected error: " + str(sys.exc_info()))
            self._logger.warning("Failed to connect to all friends.")
        else:
            self._logger.debug("No friends to connect to.")

    def touch_last_heartbeat(self, node_id):
        if node_id in self._nodes:
            self._nodes[node_id].touch_last_heartbeat()
        else:
            logging.getLogger('oand').debug("Unknown node %s is touching me." % node_id)

    def send_heartbeat(self, node):
        self._logger.debug("Send heartbeat to: " + node.get_name())
        try:
            remote_node.connect(node.get_connection_url())
            resp = remote_node.send_heartbeat(self.get_my_node().get_node_id())
            if resp.status == 'ok':
                return True
            else:
                return False
        except:
            return False

    def check_heartbeat(self):
        all_nodes_are_inactive = True
        for node_id, node in self._nodes.iteritems():
            print "test " +node_id
            if (node.is_heartbeat_expired()):
                if (self.send_heartbeat(node)):
                    self._nodes[node_id].touch_last_heartbeat()
                    all_nodes_are_inactive = False

        if all_nodes_are_inactive:
            self.connect_to_oan()

    def remove_expired_nodes(self):
        nodes_to_remove = []
        for node_id, node in self._nodes.iteritems():
            if (node.is_node_expired()):
                nodes_to_remove.append(node_id)
        for node_id in nodes_to_remove:
            del(self._nodes[node_id])

    def get_dbg_nodes(self):
        nodes = self._my_node.get_name()
        for node in self.get_nodes().itervalues():
            nodes += " - "
            nodes += node.get_name()

        return nodes