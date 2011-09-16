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

import urllib
import json
import logging

from abc import ABCMeta, abstractmethod

from networknode import NetworkNode

class Client():
    '''Abstract class for network clients'''
    __metaclass__ = ABCMeta

    _logger = None

    def __init__(self, client_name):
        self._logger = logging.getLogger('oand')

class JsonClient(Client):
    _url = None

    def connect(self, url):
        self._url = url
        self._logger.debug("Connect to " +  url)

    def get_nodes(self):
        nodes = {}
        result = self._execute("/nodes")
        if result['status'] == "ok":
            for node_id, node in result['nodes'].iteritems():
                nodes[node_id] = NetworkNode(
                    node['name'],
                    node['domain_name'],
                    node['port'],
                    node['last_heartbeat'])
        return nodes

    def send_heartbeat(self, node_id):
        return self._execute("/heartbeat/" + node_id)

    def _execute(self, cmd):
        '''
        Do a get request against the remote server, and convert the
        json result to a python dict.

        '''
        url = "http://" + self._url + cmd
        self._logger.debug("Execute %s." % url)
        f = urllib.urlopen(url)
        json_data = f.read()

        return json.loads(json_data)