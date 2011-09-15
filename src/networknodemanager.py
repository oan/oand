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

from abc import ABCMeta, abstractmethod

class NetworkNode():
    _node_id = None
    _name = None
    _domain_name = None
    _port = None
    _last_heartbeat = None

    def __init__(self, name, domain_name, port):
        self._node_id = name
        self._name = name
        self._domain_name = domain_name
        self._port = port

    def get_id(self):
        return self._node_id

    def get_name(self):
        return self._name

    def get_domain_name(self):
        return self._domain_name

    def get_port(self):
        return self._port

    def get_connection_url(self):
        return self.get_domain_name() + ':' + self.get_port()

    def is_valid(self):
        if (self.get_name() and
            self.get_domain_name() and
            self.get_port()):
            return True
        else:
            return False

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
                    self._logger.info(
                        "Connect " + self._my_node.get_name() + " with " +
                        remote_node.get_name())

                    remote_node.connect(node.get_connection_url())
                    nodes = remote_node.get_nodes()
                    self.merge_nodes(nodes)
                    return
                except:
                    pass
            self._logger.warning("Failed to connect to all friends.")
        else:
            self._logger.info("No friends to connect to.")

    def get_dbg_nodes(self):
        nodes = self._my_node.get_name()
        for node in self.get_nodes().itervalues():
            nodes += " - "
            nodes += node.get_name()

        return nodes