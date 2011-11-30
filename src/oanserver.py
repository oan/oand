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

from oannetworknode import OANNetworkNode
from oan import node_manager, meta_manager, data_manager

class OANServer():
    '''
    Creating a twisted server.

    '''
    def __init__(self, config):
        reactor.listenTCP(
            int(config.node_port),
            server.Site(
                OANRootHandler()
            )
        )
        logging.debug("Start twisted server on port %s." % config.node_port)

class OANRootHandler(resource.Resource):
    def __init__(self):
        resource.Resource.__init__(self)
        self.putChild('nodes', OANNodeListHandler())
        self.putChild('heartbeat', OANHeartbeatHandler())
        self.putChild('value', OANValueHandler())
        self.putChild('htmlvalue', OANHtmlValueHandler())
        self.putChild('meta', OANMetaHandler())
        self.putChild('', File(self.get_current_dir() + "html/index.html"))

    def getChild(self, path, request):
        return File(self.get_current_dir() + "html/404.html")

    def get_current_dir(self):
        return os.path.dirname(__file__) + "/"

class OANHandlerBase(resource.Resource):
    def __init__(self):
        self.isLeaf = True
        resource.Resource.__init__(self)

    def render_HEAD(self, request):
        return self.get_not_supported_resources()

    def render_GET(self, request):
        return self.get_not_supported_resources()

    def render_POST(self, request):
        return self.get_not_supported_resources()

    def render_PUT(self, request):
        return self.get_not_supported_resources()

    def render_DELETE(self, request):
        return self.get_not_supported_resources()

    def set_json_headers(self, request):
        request.setHeader("Server", "OAND")
        request.setHeader("Content-Type", "application/json")

    def set_html_headers(self, request):
        request.setHeader("Server", "OAND")
        request.setHeader("Content-Type", "text/html")

    def log(self, request, type = None):
        logging.getLogger('oand').debug(
            "Access log - from: %s - to: %s/%s - Agent: %s - Type: %s" % (
            request.getClientIP(),
            request.URLPath(),
            "/".join(request.postpath),
            request.getHeader("user-agent"),
            type)
        )

    def get_not_supported_resources(self):
        return File(self.get_current_dir() + "html/not-supported.html")

    def create_node_from_request(self, request):
        json_args = request.args['json'][0]
        args = json.loads(json_args)
        return OANNetworkNode.create_from_dict(args)

class OANNodeListHandler(OANHandlerBase):
    def render_nodes_result(self, request):
        self.set_json_headers(request)

        obj = {}
        obj["status"] = "ok"
        obj["nodes"] = {}

        my_node = node_manager().get_my_node()
        my_node.heartbeat.touch()
        obj["nodes"][node.uuid] = my_node.get_dict()

        for node in node_manager().get_nodes().itervalues():
            obj["nodes"][node.uuid] = node.get_dict()

        return json.dumps(obj)

    def render_GET(self, request):
        self.log(request, "get-nodes")
        return self.render_nodes_result(request)

    def render_POST(self, request):
        self.log(request, "post-nodes")

        remote_node = self.create_node_from_request(request)
        node_manager().touch_last_heartbeat(remote_node)

        return self.render_nodes_result(request)

class OANHeartbeatHandler(OANHandlerBase):
    def render_POST(self, request):
        self.log(request, "post-heartbeat")

        remote_node = self.create_node_from_request(request)
        node_manager().touch_last_heartbeat(remote_node)

        self.set_json_headers(request)
        obj = {}
        obj["status"] = "ok"
        return json.dumps(obj)

class OANValueHandler(OANHandlerBase):
    def _get_key(self, request):
        return "/".join(request.postpath)

    def render_GET(self, request):
        key = self._get_key(request)
        self.log(request, "get-value")

        self.set_json_headers(request)
        obj = {}

        if (data_manager().exist(key)):
            request.setResponseCode(http.FOUND)
            obj["status"] = "ok"
            obj["type"] = "get-value"
            obj["key"] = key
            obj["value"] = data_manager().get(key)
        else:
            request.setResponseCode(http.NOT_FOUND)
            obj["status"] = "fail"
            obj["type"] = "get-value"
            obj["key"] = key
            obj["value"]  = ""

        return json.dumps(obj)

    def render_POST(self, request):
        key = self._get_key(request)
        self.log(request, "post-value")

        value = request.args['value'][0]
        data_manager().set(key, value)

        self.set_json_headers(request)
        request.setResponseCode(http.FOUND)
        obj = {}
        obj["status"] = "ok"
        obj["key"] = key
        obj["value"] = "post-value"
        return json.dumps(obj)

    def render_DELETE(self, request):
        key = self._get_key(request)
        self.log(request, "delete-value")

        if data_manager().exist(key):
            data_manager().delete(key)
            status =  "ok"
        else:
            status = "fail"

        self.set_json_headers(request)
        request.setResponseCode(http.FOUND)
        obj = {}
        obj["status"] = status
        obj["key"] = key
        obj["value"] = "delete-value"
        return json.dumps(obj)

class OANHtmlValueHandler(OANValueHandler):
    def get_html_file_form(self, resource):
        return """
        <html><body>Use post method for direct insertion or form below<br>
        <form action='/htmlvalue/%s' method=POST>
        Key: %s<br/>
        <textarea cols="40" rows="20" name=value>%s</textarea><br>
        <input type="submit" name="save" value="Save">
        <input type="submit" name="delete" value="Delete">
        </body></html>
        """ % (resource.path, resource.path, resource.value)

    def get_html_folder_form(self, resource):
        """View resources in a folder"""
        html = "<html><body>Folders in: %s<br>" % (resource.path)

        for path in resource.value:
            html += '<a href="/htmlvalue/%s">%s</a><br/>' % (path, path)

        html += '</body></html>'
        return html

    def render_GET(self, request):
        key = self._get_key(request)
        self.log(request, "get-html-value")

        self.set_html_headers(request)

        if (data_manager().exist(key)):
            request.setResponseCode(http.FOUND)
            resource = data_manager().get(key)
        else:
            request.setResponseCode(http.NOT_FOUND)
            resource = Resource(path = key, value="Default")

        if (resource.is_file(key)):
            return self.get_html_file_form(resource)
        elif (resource.is_folder(key)):
            return self.get_html_folder_form(resource)

    def render_POST(self, request):
        key = self._get_key(request)

        self.set_html_headers(request)
        request.setResponseCode(http.FOUND)

        if ("delete" in request.args):
            self.log(request, "delete-html-value")
            value = "Default"
            data_manager().delete(key)
        else:
            self.log(request, "post-html-value")
            value = request.args['value'][0]
            data_manager().set(key, value)

        return self.get_html_form(key, value)

    def render_DELETE(self, request):
        return "Not implemented"

class OANMetaHandler(OANHandlerBase):
    def _get_key(self, request):
        return "/".join(request.postpath)

    def render_GET(self, request):
        self.log(request, "get-meta")

        self.set_json_headers(request)
        obj = {}

        key = '/' + self._get_key(request)
        if (meta_manager().resourceRoot.exist(key)):
            request.setResponseCode(http.FOUND)
            obj["status"] = "ok"
            obj["type"] = "get-meta"
            obj["key"] = key
            obj["value"] = meta_manager().get(key).get_dict()
        else:
            request.setResponseCode(http.NOT_FOUND)
            obj["status"] = "fail"
            obj["type"] = "get-meta"
            obj["key"] = key
            obj["value"]  = ""

        return json.dumps(obj)
