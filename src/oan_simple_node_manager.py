import asyncore
import socket
import time
import datetime
import thread
from threading import Thread
from threading import Timer
from Queue import Queue

class OANNode:
    node_id = None
    port = None
    host = None

    last_connect_success = None
    last_connect_fail = None

    out_queue = Queue()
    in_queue = Queue()

    def __init__(self, node_id, host, port):
        self.node_id = node_id
        self.host = host
        self.port = port

class OANNodeManager():
    server = None
    nodes = {}

    def __init__(self, server):
        self.server = server

    def add_node(self, node):
        self.nodes[node.node_id] = node

    def exist_node(self, node_id):
        return (node_id in self.nodes)

    def get_node(self, node_id):
        return self.nodes[node_id]

    def send(self, node_id, message):
        if (node_id in self.nodes):
            node = self.nodes[node_id]
            node.out_queue.put(message)

        if (node_id not in self.server.bridges):
            self.server.connect_to_node(node)
