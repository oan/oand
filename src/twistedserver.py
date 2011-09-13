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

from iclientserver.py import Server

class TwistedServer(Server):
    '''
    Creating a twisted server.

    '''

    _logger = None
    _network_node = None
    _data_store_manager = None

    def __init__(self, network_node, data_store_manager):
        self._logger = logging.getLogger('oand' + network_node.get_name())
        self._network_node = network_node
        self._data_store_manager = data_store_manager
        self.start()

    def start(self):
        '''Start server and listen on port xx for incoming tcp/ip requests'''
        self._logger.debug("Start twisted server")
        reactor.listenTCP(8082, server.Site(RootResource(self.data_store_manager)))
        reactor.run()

    def add_node(self, name, domain_name, port):
        pass

    def set_prev_node(self, name, domain_name, port):
        pass

    def set_next_node(self, name, domain_name, port):
        pass

class RootResource(resource.Resource):
    def __init__(self, data_store_manager):
        self._data_store_manager = data_store_manager
        resource.Resource.__init__(self)
        self.putChild('value', MessageHandler(self._data_store_manager))
        self.putChild('', File("html/index.html"))

    def getChild(self, path, request):
        logging.getLogger('oandtwisted').debug("root: " + path)
        return File("html/404.html")

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

        if (self._data_store_manager.hasMessage(filename)):
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
