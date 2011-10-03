#!/usr/bin/env python
'''
Interfaces/Abstract classes for handling connections between client and servers.

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import logging
from abc import ABCMeta, abstractmethod

class Client():
    '''Abstract class for network clients'''
    __metaclass__ = ABCMeta

    _logger = None

    def __init__(self, client_name):
        self._logger = logging.getLogger('oand')

    @abstractmethod
    def connect(self, connection_url):
        pass

class Server():
    '''Abstract class for network servers'''
    __metaclass__ = ABCMeta
    _logger = None


    def __init__(self, network_node):
        self._logger = logging.getLogger('oand')
        self._network_node = network_node
        self.start()

    @abstractmethod
    def start(self):
        '''Start server and listen on port xx for incoming tcp/ip requests'''
        pass