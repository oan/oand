import asyncore
import socket
import time
import datetime
import thread
from threading import Thread
from threading import Timer
from Queue import Queue

class OANNode:

    heartbeat = None
    uuid = None
    name = None
    port = None
    host = None

    out_queue = Queue()
    in_queue = Queue()

    def __init__(self, uuid, host, port):
        self.uuid = uuid
        self.host = host
        self.port = port

class OANNodeManager():
    server = None
    nodes = {}

    def __init__(self, server):
        self.server = server

    def create_node(self, uuid, host, port):
        node = OANNode(uuid, host, port);
        self.nodes[uuid] = node
        return node

    def add_node(self, node):
        self.nodes[node.uuid] = node
        return node

    def exist_node(self, uuid):
        return (uuid in self.nodes)

    def get_node(self, uuid):
        return self.nodes[uuid]

    def send(self, uuid, message):
        if (uuid in self.nodes):
            node = self.nodes[uuid]
            node.out_queue.put(message)

        if (uuid not in self.server.bridges):
            self.server.connect_to_node(node)

