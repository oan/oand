import asyncore
import socket
import time
import datetime
import thread
from threading import Thread
from threading import Timer
from Queue import Queue

from oan_heartbeat import OANHeartbeat
from oan_message import OANMessageDispatcher

class OANNode:
    heartbeat = OANHeartbeat()
    uuid = None
    name = None
    port = None
    host = None

    out_queue = None

    def __init__(self, uuid, host, port):
        self.out_queue = Queue()
        self.uuid = uuid
        self.host = host
        self.port = port

class OANNodeManager():
    # Node server to connect and send message to other node servers
    _server = None
    dispatcher = None

    # Info about my own node.
    _my_node = None

    # An dictionary with all nodes in the OAN.
    _nodes = {}

    def create_node(self, uuid, host, port):
        node = OANNode(uuid, host, port);
        self._nodes[uuid] = node
        return node

    def set_my_node(self, node):
        from oan_server import OANServer

        self.dispatcher = OANMessageDispatcher()
        self.dispatcher.start()

        self._my_node = node
        self._server = OANServer(node.host, node.port)


    def get_my_node(self):
        return self._my_node

    def add_node(self, node):
        self._nodes[node.uuid] = node
        return node

    def exist_node(self, uuid):
        return (uuid in self._nodes)

    def get_node(self, uuid):
        return self._nodes[uuid]

    def send(self, uuid, message):
        if (uuid in self._nodes):
            node = self._nodes[uuid]
            node.out_queue.put(message)

        if (uuid not in self._server.bridges):
            self._server.connect_to_node(node)


    def shutdown(self):
        self._server.shutdown()
        self.dispatcher.stop()


