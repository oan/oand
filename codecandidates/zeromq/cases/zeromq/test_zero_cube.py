#!/usr/bin/env python


from time import sleep, time
from threading import Thread, Event
from Queue import Queue
import json

import sys
import os

import zmq
from random import randrange, randint

from oan.util.daemon_base import OANDaemonBase
from oan.util.signal_handler import OANSignalHandler, OANTerminateInterrupt
from oan.util import log
from test.test_case import OANTestCase

# Files used in test.
F_PID="/tmp/ut_zeromq_daemon%s.pid"
F_OUT="/tmp/ut_zeromq_daemon%s.out"
F_ERR="/tmp/ut_zeromq_daemon%s.err"
F_DWN="/tmp/ut_zeromq_daemon%s.down"

"""
x

xx

xxxx

xxxx
x

xxxx



xxxxx
xxxxx
xxxxx
xxxxx
xxxxx


"""

class ZeroCube:
    x_max = 100
    y_max = 100
    z_max = 100

    x_list = None
    y_list = None
    z_list = None

    def __init__(self):
        self.x_list = []
        self.y_list = []
        self.z_list = []

    def add(self, node):
        if self._add_to_list(node, self.x_list):
            return True

        if self._add_to_list(node, self.y_list):
            return True

        if self._add_to_list(node, self.z_list):
            return True

        return False

    def _add_to_list(self, node, node_list):
        if len(node_list) < self.x_max:
            node_list.append(node)
            node_list.sort()
            return True

class ZeroNode:
    cube = None

    def __init__(self):
        self.cube = ZeroCube()

    def add(self, node):
        self.cube.add(node)

class TestZeroCube(OANTestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_add(self):


