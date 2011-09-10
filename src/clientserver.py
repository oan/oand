#!/usr/bin/env python
'''
Handles connections between client and servers.

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from abc import ABCMeta, abstractmethod

class Client():
    '''Abstract class for network clients'''
    __metaclass__ = ABCMeta

    @abstractmethod
    def connect(self, connection_url):
        pass

    @abstractmethod
    def add_node(self, name, domain_name, port):
        pass

    @abstractmethod
    def set_prev_node(self, name, domain_name, port):
        pass

    @abstractmethod
    def set_next_node(self, name, domain_name, port):
        pass

class Server():
    '''Abstract class for network servers'''
    __metaclass__ = ABCMeta

    def __init__(self, network_node):
        self._network_node = network_node
        self.start()

    @abstractmethod
    def start(self):
        '''Start server and listen on port xx for incoming tcp/ip requests'''
        pass

    @abstractmethod
    def add_node(self, name, domain_name, port):
        pass

    @abstractmethod
    def set_prev_node(self, name, domain_name, port):
        pass

    @abstractmethod
    def set_next_node(self, name, domain_name, port):
        pass

SERVERS = {}

class LocalNetworkServer(Server):
    _network_node = None

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

class LocalNetworkClient(Client):
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

