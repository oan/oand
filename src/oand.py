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
import logging, sys
import logging.handlers

from networknode import CircularNetworkNode
from objectclientserver import ObjectClient, ObjectServer

class OAND():
    _network_node = None
    _config = None
    _server = None

    def __init__(self, config, network_node_class, server_class, client_class):
        self._start_logger(config.get_server_name())

        self._logger.info("Starting Open Archive Network (oand)")
        self._logger.debug("network_node_class " + str(network_node_class))
        self._logger.debug("server_class " + str(server_class))
        self._logger.debug("client_class " + str(client_class))

        self._config = config

        self._network_node = network_node_class(
            client_class,
            self._config.get_server_name(),
            self._config.get_server_domain_name(),
            self._config.get_server_port())

        self._server = server_class(self._network_node)

        if (self._config.get_bff_name()):
            bff_node = network_node_class(
                client_class,
                self._config.get_bff_name(),
                self._config.get_bff_domain_name(),
                self._config.get_bff_port())

            self._network_node.join_remote_server(bff_node)

        self.dbg_print_network()
        self._logger.info("Stopping Open Archive Network (oand)")

    @classmethod
    def create_localnetwork_circular_node(cls, config):
        return cls(config, CircularNetworkNode,
                   ObjectServer, ObjectClient)

    def get_network_node(self):
        return self._network_node

    def dbg_print_network(self):
        self._logger.debug("Nodes in network on " + self._network_node.get_name())
        self._logger.debug(self._network_node.get_dbg_nodes())

    def _start_logger(self, server_name):
        # create logger
        self._logger = logging.getLogger('oand' + server_name)
        self._logger.setLevel(logging.DEBUG)

        # create console handler and set level to debug
        ch1 = logging.handlers.SysLogHandler()
        ch1.setLevel(logging.DEBUG)
        ch2 = logging.handlers.RotatingFileHandler("../log/oand.log", maxBytes=2000000, backupCount=100)
        ch2.setLevel(logging.DEBUG)

        # create formatter
        formatter = logging.Formatter(
            '%(asctime)s - oand (' + server_name + ') - %(message)s')

        # add formatter to ch
        ch1.setFormatter(formatter)
        ch2.setFormatter(formatter)

        # add ch to logger
        self._logger.addHandler(ch1)
        self._logger.addHandler(ch2)
