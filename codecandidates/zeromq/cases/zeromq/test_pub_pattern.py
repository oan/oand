#!/usr/bin/env python



import requests
from time import sleep
from threading import Thread
import sys

import zmq
import random

from oan.util.daemon_base import OANDaemonBase
from oan.util.signal_handler import OANSignalHandler, OANTerminateInterrupt
from test.test_case import OANTestCase
from oan.util import log


class ZeroMessageNodeList:
    node_list = None

    def __init__(self, node_list):
        self.node_list = node_list


class ZeroConnection:
    origin = None
    destination = None

    def __init__(self, origin, destination):
        self.origin = origin
        self.destination = destination

    def send(self, message):
        self.destination.receive(message)


class ZeroManager:
    connections = {}

class ZeroNode:
    x_list = None
    y_list = None
    z_list = None

    incomming = None
    outgoing = None
    slot_id = None
    oan_id = None

    def __init__(self, oan_id):
        self.x_list = []
        self.y_list = []
        self.z_list = []

        self.x_list.append(self)
        self.y_list.append(self)
        self.z_list.append(self)

        self.slot_id = (0, 0, 0)

        self.connections = []

    def connect(self):
        self.connections.append(self._get_connections(self.x_list))
        self.connections.append(self._get_connections(self.y_list))
        self.connections.append(self._get_connections(self.z_list))

    def send(self, message):
        pass

    def receive(self, message):
        pass

    def _get_connection(self, node_list):
        """ gets one node far away from your own node """
        idx = node_list.index(self) + (len(node_list)) / 2
        yield ZeroConnection(self, node_list[idx-1])

        """ gets near your own node """
        idx = node_list.index(self)
        if idx > len(node_list) - 2:
            idx = 0
        yield ZeroConnection(self, node_list[idx+1])
        yield ZeroConnection(self, node_list[idx+2])


class TestZeroCube(OANTestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass


    def route(self, origin, destination, route_table, path, current_depth = 0, max_depth=10):

        path.append(origin)

        if origin not in route_table:
            return False

        p = route_table[origin]
        if destination in p:
            log.info("found %s=>%s depth:%s" % (origin, destination, current_depth))
            path.append(destination)
            return True

        for k in p:
            log.info("routing %s=>%s depth:%s" % (origin, k, current_depth))

            if (current_depth == max_depth):
                return False

            if self.route(k, destination, route_table, path, current_depth+1, max_depth):
                return True

    # du lyssnar lång bort och publiserar nära
    def test_node_connections(self):
        result = {}

        concurrent = 4
        number_of_nodes = 100
        jump = number_of_nodes / (concurrent+1)

        for o in xrange(0, number_of_nodes):
            for c in xrange(0, concurrent):
                d = o + (c % jump) + 1
                log.info("%s:%s" % (o, d))

                if o not in result:
                    result[o] = {}

                if d != o:
                    result[o][d] = "Forward"

        log.info(result)

        #for o in xrange(1, 2):
        #    for d in xrange(99, 100):
        #        if (o != d):

        o = 0
        d = 552
        path = []
        #log.info("route (%s-%s) total:%s" % (o, d, self.route(o, d, result, path)))
        log.info(path)




