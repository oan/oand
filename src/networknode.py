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
    '''Abstract class for Networknodes'''
    __metaclass__ = ABCMeta

    _client_class = None
    _name = None
    _domain_name = None
    _port = None

    _logger = None

    def __init__(self, client_class, name, domain_name, port):
        self._client_class = client_class
        self._name = name
        self._domain_name = domain_name
        self._port = port
        self._logger = logging.getLogger('oand' + name)

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

    @abstractmethod
    def join_remote_server(self, remote_node):
        pass

    @abstractmethod
    def add_node(self, name, domain_name, port):
        pass

class CircularNetworkNode(NetworkNode):
    _prev_node = None
    _next_node = None

    def join_remote_server(self, remote_node):
        if (remote_node.is_valid()):
            self._logger.info("Connect " + self.get_name() + " with " +
                              remote_node.get_name())

            remote_server = self._client_class(self.get_name())
            remote_server.connect(remote_node.get_connection_url())
            remote_server.add_node(
                self.get_name(), self.get_domain_name(), self.get_port())
        else:
            print "Nobody to join"

    def add_node(self, name, domain_name, port):
        remote_node = CircularNetworkNode(self._client_class,
                                          name, domain_name, port)

        if (self._prev_node == None and self._next_node == None):
            old_prev_node = self
            self._next_node = remote_node
            self._prev_node = remote_node
        elif self._prev_node.get_name() != remote_node.get_name():
            old_prev_node = self._prev_node
            self._prev_node.set_remote_next_node(remote_node)
            self._prev_node = remote_node

        remote_node.set_remote_prev_node(old_prev_node)
        remote_node.set_remote_next_node(self)

    def set_prev_node(self, name, domain_name, port):
        self._prev_node = CircularNetworkNode(self._client_class,
                                              name, domain_name, port)

    def set_next_node(self, name, domain_name, port):
        self._next_node = CircularNetworkNode(self._client_class,
                                              name, domain_name, port)

    def set_remote_prev_node(self, remote_node):
        # @todo self.set_prev_node(remote_node) need to be executed, 
	# can't create new node.
        self.set_prev_node(remote_node.get_name(),
                           remote_node.get_domain_name(),
                           remote_node.get_port())

        client = self._client_class(self.get_name())
        client.connect(self.get_connection_url())
        client.set_prev_node(remote_node.get_name(),
                             remote_node.get_domain_name(),
                             remote_node.get_port())

    def set_remote_next_node(self, remote_node):
        self.set_next_node(remote_node.get_name(),
                           remote_node.get_domain_name(),
                           remote_node.get_port())

        client = self._client_class(self.get_name())
        client.connect(self.get_connection_url())
        client.set_next_node(remote_node.get_name(),
                             remote_node.get_domain_name(),
                             remote_node.get_port())

    def get_dbg_nodes(self):
        out = ""
        if (self._prev_node):
            out += self._prev_node.get_name()
        else:
            out += 'None'

        out += ' - ' + self.get_name() + ' - '

        if (self._next_node):
            out += self._next_node.get_name()
        else:
            out += 'None'

        return out

    def dbg_walk(self, start_node = None):
        if (start_node != self):
            if (start_node == None):
                start_node = self
            else:
                print self.get_name()
            if (self._next_node):
                self._next_node.dbg_walk(start_node)
            else:
                print "None"
