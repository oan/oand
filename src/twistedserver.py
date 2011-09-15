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
import json
import os

from twisted.web import server, resource, http
from twisted.internet import reactor
from twisted.web.static import File

from Iclientserver import Server

class TwistedServer(Server):
    '''
    Creating a twisted server.

    '''
    _logger = None
    _network_nodes_manager = None
    _data_store_manager = None

    def __init__(self, network_nodes_manager, data_store_manager):
        self._logger = logging.getLogger('oand' + network_nodes_manager.get_my_node().get_name())
        self._network_nodes_manager = network_nodes_manager
        self._data_store_manager = data_store_manager
        self.start()

    def start(self):
        '''Start server and listen on port xx for incoming tcp/ip requests'''
        self._logger.debug("Start twisted server")
        reactor.listenTCP(8082, server.Site(RootResource(self._data_store_manager, self._network_nodes_manager)))
        reactor.run()

    def add_node(self, name, domain_name, port):
        pass

    def set_prev_node(self, name, domain_name, port):
        pass

    def set_next_node(self, name, domain_name, port):
        pass

class RootResource(resource.Resource):
    def __init__(self, data_store_manager, network_nodes_manager):
        resource.Resource.__init__(self)
        self.putChild('nodes', NodeListHandler(network_nodes_manager))
        self.putChild('value', MessageHandler(data_store_manager))
        self.putChild('', File(self.get_current_dir() + "html/index.html"))

    def getChild(self, path, request):
        return File(self.get_current_dir() + "html/404.html")

    def get_current_dir(self):
        return os.path.dirname(__file__) + "/"

class NodeListHandler(resource.Resource):
    _network_nodes_manager = None

    def __init__(self, network_nodes_manager):
        self._network_nodes_manager = network_nodes_manager
        self.isLeaf=True
        resource.Resource.__init__(self)

    def render_GET(self, request):
        request.setHeader("Server", "OAND")
        request.setHeader("Content-Type", "application/json")
        request.setResponseCode(http.FOUND)
        obj = {}
        obj["status"] = "ok"
        obj["nodes"] = {}
        for node in self._network_nodes_manager.get_nodes().itervalues():
            obj["nodes"][node.get_id()] = {}
            obj["nodes"][node.get_id()]['name'] = node.get_name()
            obj["nodes"][node.get_id()]['domain_name'] = node.get_domain_name()
            obj["nodes"][node.get_id()]['port'] = node.get_port()
            obj["nodes"][node.get_id()]['last_heartbeat'] = node.get_last_heartbeat()

        return json.dumps(obj)

    def render_POST(self, request):
        return File(self.get_current_dir() + "html/not-supported.html")

    def render_DELETE(self, request):
        return File(self.get_current_dir() + "html/not-supported.html")

class MessageHandler(resource.Resource):
    def __init__(self, data_store_manager):
        self._data_store_manager = data_store_manager
        self.isLeaf=True
        resource.Resource.__init__(self)

    def _get_filename(self, request):
        return "/".join(request.postpath)

    def render_GET(self, request):
        request.setHeader("Server", "OAND")
        filename = self._get_filename(request)
        logging.getLogger('oandtwisted').debug("value: " + filename)

        if (self._data_store_manager.exist(filename)):
            request.setHeader("Content-Type", "application/json")
            request.setResponseCode(http.FOUND)
            obj = {}
            obj["filename"] = filename
            obj["data"] = self._data_store_manager.get(filename)
            return json.dumps(obj)
        else:
            request.setHeader("Content-Type", "text/html")
            request.setResponseCode(http.NOT_FOUND)
            return """
            <html><body>use post method for direct insertion or form below<br>
            <form action='/value/%s' method=POST>
            <textarea name=body>Body</textarea><br>
            <input type=submit>
            </body></html>
            """ % filename

    def render_POST(self, request):
        filename = self._get_filename(request)
        body=request.args['body'][0]
        self._data_store_manager.set(filename, body)
        return "Posted"

    def render_DELETE(self, request):
        if self._data_store_manager.exist(self.path):
            self._data_store_manager.delete(self.path)
            return """ msg %s deleted	""" % (self.path)
        else:
            return """ msg not found for hashKey: %s""" % self.path
