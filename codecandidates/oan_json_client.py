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

from oan.network_node import OANNetworkNode

class OANURLopener(urllib.FancyURLopener):
    '''
    Set user agent for all client requests.

    '''
    version = "OAND/0.1"

urllib._urlopener = OANURLopener()

class OANClient():
    _url = None

    def connect(self, url):
        self._url = url

    def get_nodes(self, node):
        result = self._execute_post("/nodes", node.get_dict())
        nodes = {}
        if result['status'] == "ok":
            for node_id, node in result['nodes'].iteritems():
                nodes[node_id] = OANNetworkNode(
                    node['uuid'],
                    node['name'],
                    node['domain_name'],
                    node['port'],
                    node['last_heartbeat']
                )
        return nodes

    def send_heartbeat(self, node):
        return self._execute_post("/heartbeat", node.get_dict())

    def get_resource(self, node, path):
        return self._execute_post("/resource/%s" % path, node.get_dict())

    def _execute_post(self, cmd, param):
        '''
        Do a POST request against the remote server, and convert the
        json result to a python dict.

        '''
        json_param = "json=" + json.dumps(param)

        url = "http://" + self._url + cmd
        logging.debug("Execute: curl -X POST -d '%s' %s" % (json_param, url))
        f = urllib.urlopen(url, json_param)
        json_data = f.read()
        logging.debug("  Result: %s" % (json_data))
        return json.loads(json_data)
