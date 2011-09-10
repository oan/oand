#!/usr/bin/env python
'''
Proof of concept of distributed nosql database/filesystem.

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from config import Config

from networknode import CircularNetworkNode
from clientserver import LocalNetworkClient, LocalNetworkServer

class OAND():
    _network_node = None
    _config = None
    _server = None

    def __init__(self, config, network_node_class, server_class, client_class):
        self._config = config

        self._network_node = network_node_class(
            client_class,
            self._config.get_server_name(),
            self._config.get_server_domain_name(),
            self._config.get_server_port())

        bff_node = network_node_class(
            client_class,
            self._config.get_bff_name(),
            self._config.get_bff_domain_name(),
            self._config.get_bff_port())

        self._server = server_class(self._network_node)

        self._network_node.join_remote_server(bff_node)

        self.dbg_print_network()

    @classmethod
    def create_localnetwork_circular_node(cls, config):
        return cls(config, CircularNetworkNode,
                   LocalNetworkServer, LocalNetworkClient)

    def get_network_node(self):
        return self._network_node

    def dbg_print_network(self):
        print "Nodes in network on " + self._network_node.get_name()
        print self._network_node.get_dbg_nodes()
        print