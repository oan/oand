import asyncore
import socket
import time
import datetime
import thread
from threading import Thread
from threading import Timer
from Queue import Queue

from oan_heartbeat import OANHeartbeat
from oan_message import OANMessageDispatcher, OANMessageNodeSync, OANMessageHeartbeat

class OANNetworkNodeState:
    connecting, connected, disconnected = range(1, 4)

class OANNetworkNode:
    heartbeat = None
    uuid = None
    name = None
    port = None
    host = None
    state = None
    blocked = None # if server is listen or its blocked by router or firewall.

    out_queue = None

    def __init__(self, uuid, host, port):
        self.blocked = False
        self.state = OANNetworkNodeState.disconnected
        self.heartbeat = OANHeartbeat()
        self.out_queue = Queue()
        self.uuid = uuid
        self.host = host
        self.port = port

class OANNodeManager():
    # Node server to connect and send message to other node servers
    server = None
    dispatcher = None

    # Info about my own node.
    _my_node = None

    # A dictionary with all nodes in the OAN.
    _nodes = {}

    def create_node(self, uuid, host, port):
        if self.exist_node(uuid):
            node = self._nodes[uuid]
            node.host = host
            node.port = int(port)
        else:
            node = OANNetworkNode(uuid, host, int(port));
            self._nodes[uuid] = node

        node.heartbeat.touch()
        return node

    def set_my_node(self, node):
        if self._my_node is None:
            from oan_server import OANServer
            self.dispatcher = OANMessageDispatcher()
            self.dispatcher.start()
            self.server = OANServer()
            self.server.start_listen(node)
            self._my_node = node
        else:
            print "OANNodeManager:Error my node is already set"

    def get_my_node(self):
        return self._my_node

    def add_node(self, node):
        self._nodes[node.uuid] = node
        return node

    def exist_node(self, uuid):
        return (uuid in self._nodes)

    def get_node(self, uuid):
        return self._nodes[uuid]

    def send_heartbeat(self):
        heartbeat = OANMessageHeartbeat.create(self._my_node)
        for n in self._nodes.values():
            if n.uuid != heartbeat.uuid:
                if n.heartbeat.is_expired():
                    self.send(n.uuid, heartbeat)

    def send_node_sync(self):
        node_sync = OANMessageNodeSync.create()
        for n in self._nodes.values():
            if n.uuid != node_sync.node_uuid:
                self.send(n.uuid, node_sync)

    def send(self, uuid, message):
        if (uuid in self._nodes):
            node = self._nodes[uuid]
            node.out_queue.put(message)
        else:
            print "OANNodeManager:Error node is missing %s" % uuid

        # it will only try if the bridge is not open
        if (node.state == OANNetworkNodeState.disconnected):
            self.server.connect_to_node(node)

    def shutdown(self):
        self.server.shutdown()
        self.dispatcher.stop()


