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

    def __init__(self, node_id, host, port):
        self.node_id = node_id
        self.host = host
        self.port = port

class OANNodeManager(Thread):

    server = None
    nodes = {}
    queue = Queue()

    _running = False

    def __init__(self, server):
        Thread.__init__(self)
        self.server = server


    def add_node(self, node):
        self.nodes[node.node_id] = node

    def send(self, node_id, message):
        self.queue.put((node_id, message))

    def start(self):
        if (not self._running):
            self._running = True
            Thread.start(self)

    def stop(self):
        self._running = False

    def run(self):
        print "OANNodeManager: started"
        while(self._running):
            (node_id, message) = self.queue.get() # waiting for a message
            if (node_id in self.nodes):
                node = self.nodes[node_id]

                if (node_id in self.server.bridges):
                    print "OANNodeManager: is connected"
                    bridge = self.server.bridges[node_id]
                else:
                    print "OANNodeManager: not connected"
                    self.server.connect_to_node(node) # try to reconnect to node
                    Timer(5, self.send, (node_id, message)).start()

            print "OANNodeManager: check if running"

        print "OANNodeManager stopped"
