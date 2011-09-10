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

from abc import ABCMeta, abstractmethod

from config import Config

class NetworkNode():
    '''Abstract class for Networknodes'''
    __metaclass__ = ABCMeta

    _name = None
    _domain_name = None
    _port = None

    def __init__(self, name, domain_name, port):
        self._name = name
        self._domain_name = domain_name
        self._port = port

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
            print("Connect " + self.get_name() + " with " +
                  remote_node.get_name())

            remote_server = Client()
            remote_server.connect(remote_node.get_connection_url())
            remote_server.add_node(
                self.get_name(), self.get_domain_name(), self.get_port())
        else:
            print "Nobody to join"

    def add_node(self, name, domain_name, port):
        remote_node = CircularNetworkNode(name, domain_name, port)

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
        self._prev_node = CircularNetworkNode(name, domain_name, port)

    def set_next_node(self, name, domain_name, port):
        self._next_node = CircularNetworkNode(name, domain_name, port)

    def set_remote_prev_node(self, remote_node):
        self.set_prev_node(remote_node.get_name(),
                           remote_node.get_domain_name(),
                           remote_node.get_port())

        client = Client()
        client.connect(self.get_connection_url())
        client.set_prev_node(remote_node.get_name(),
                             remote_node.get_domain_name(),
                             remote_node.get_port())

    def set_remote_next_node(self, remote_node):
        self.set_next_node(remote_node.get_name(),
                           remote_node.get_domain_name(),
                           remote_node.get_port())

        client = Client()
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

SERVERS = {}

class Client():

    _server = None

    def connect(self, connection_url):
        global SERVERS
        print "Connect to " + connection_url
        self._server = SERVERS[connection_url]

    def add_node(self, name, domain_name, port):
        self._server.add_node(name, domain_name, port)

    def set_prev_node(self, name, domain_name, port):
        self._server.set_prev_node(name, domain_name, port)

    def set_next_node(self, name, domain_name, port):
        self._server.set_next_node(name, domain_name, port)

class Server():
    _network_node = None

    def __init__(self, network_node):
        self._network_node = network_node
        self.start()

    def start(self):
        '''Start server and listen on port xx for incoming tcp/ip requests'''
        global SERVERS

        print "Start server on " + self._network_node.get_connection_url()
        SERVERS[self._network_node.get_connection_url()] = self

    def add_node(self, name, domain_name, port):
        self._network_node.add_node(name, domain_name, port)

    def set_prev_node(self, name, domain_name, port):
        self._network_node.set_prev_node(name, domain_name, port)

    def set_next_node(self, name, domain_name, port):
        self._network_node.set_next_node(name, domain_name, port)

class OAND():
    _network_node = None
    _config = None
    _server = None

    def start_deamon(self, network_node_class, config):
        self._config = config
        self._network_node = network_node_class(
            self._config.get_server_name(),
            self._config.get_server_domain_name(),
            self._config.get_server_port())

        bff_node = network_node_class(
            self._config.get_bff_name(),
            self._config.get_bff_domain_name(),
            self._config.get_bff_port())

        self._server = Server(self._network_node)
        self._network_node.join_remote_server(bff_node)

        self.dbg_print_network()

    def get_network_node(self):
        return self._network_node

    def dbg_print_network(self):
        print "Nodes in network on " + self._network_node.get_name()
        print self._network_node.get_dbg_nodes()
        print