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
class AppURLopener(urllib.FancyURLopener):
    version = "OAND/0.1"
urllib._urlopener = AppURLopener()

import json
import logging

from abc import ABCMeta, abstractmethod

from networknode import NetworkNode

class Client():
    '''Abstract class for network clients'''
    __metaclass__ = ABCMeta

    _logger = None

    def __init__(self):
        self._logger = logging.getLogger('oand')

class JsonClient(Client):
    _url = None

    def connect(self, url):
        self._url = url

    def get_nodes(self, node):
        result = self._execute_post("/nodes", node.get_dict())
        nodes = {}
        if result['status'] == "ok":
            for node_id, node in result['nodes'].iteritems():
                nodes[node_id] = NetworkNode(
                    node['name'],
                    node['domain_name'],
                    node['port'],
                    node['last_heartbeat'])
        return nodes

    def send_heartbeat(self, node):
        return self._execute_post("/heartbeat", node.get_dict())

    def _execute_post(self, cmd, param):
        '''
        Do a POST request against the remote server, and convert the
        json result to a python dict.

        '''
        json_param = "json=" + json.dumps(param)

        url = "http://" + self._url + cmd
        self._logger.debug("Execute: curl -X POST -d '%s' %s" % (json_param, url))
        f = urllib.urlopen(url, json_param)
        json_data = f.read()
        self._logger.debug("  Result: %s" % (json_data))
        return json.loads(json_data)