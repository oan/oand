#!/usr/bin/env python
"""
Test cases for oan.network.bridge

"""

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import asyncore
from threading import Thread
from Queue import Queue

from test.test_case import OANTestCase
from oan.util import log
from oan.util.daemon_base import OANDaemonBase
from oan.util.signal_handler import OANTerminateInterrupt
from oan.network.server import OANListen
from oan.network.bridge import OANBridge
from oan.network import serializer


def start_asyncore_loop():
    log.info("Start asyncore loop")
    t = Thread(target=asyncore.loop, kwargs={'timeout':0.1})
    t.name="asynco"
    t.daemon = True
    t.start()


class MessageTest():
    def __init__(self, text = None):
        self.status = "ok"
        self.text = text


class ServerNodeDaemon(OANDaemonBase):
    close_done = None
    def run(self):
        self.close_done = False
        serializer.add(MessageTest)
        bridge = OANBridge()
        bridge.out_queue = Queue()
        bridge.out_queue.put(MessageTest("Hello world"))
        bridge.connect("localhost", 1338)
        bridge.received_callback = self.received_cb
        bridge.close_callback = self.close_cb
        start_asyncore_loop()
        while not self.close_done:
            pass
        log.info("ServerNodeDaemon:run end")

    def received_cb(self, bridge, message):
        bridge.shutdown()

    def close_cb(self, bridge):
        log.info("ServerNodeDaemon:close_cb")
        self.close_done = True


class TestOANBridge(OANTestCase):
    # Remote node to test network against.
    daemon = None

    # Callback counters
    accept_counter = None
    connect_counter = None
    received_counter = None
    close_counter = None

    def setUp(self):
        serializer.add(MessageTest)

        self.daemon = ServerNodeDaemon(
            "/tmp/oand_ut_daemon.pid", stdout='/tmp/ut_out.log',
            stderr='/tmp/ut_err.log')
        self.accept_counter = 0
        self.connect_counter = 0
        self.received_counter = 0
        self.close_counter = 0

    def tearDown(self):
        self.daemon.stop()

    def accept_cb(self, bridge):
        log.info("ServerNodeDaemon::accept")
        bridge.out_queue = Queue()
        bridge.connect_callback = self.connect_cb
        bridge.received_callback = self.received_cb
        bridge.close_callback = self.close_cb

    def connect_cb(self, bridge):
        self.connect_counter += 1

    def received_cb(self, bridge, message):
        if message.__class__.__name__ == 'MessageTest':
            self.received_counter += 1
            bridge.out_queue.put(MessageTest(message.text))

    def close_cb(self, bridge):
        self.close_counter += 1

    def test_bridge(self):
        listen = OANListen("localhost", 1338, self.accept_cb)
        start_asyncore_loop()

        self.daemon.start()
        self.assertTrueWait(lambda : self.received_counter == 1)
        self.assertTrueWait(lambda : self.close_counter == 1)
        self.assertTrueWait(lambda : self.connect_counter == 0)

        listen.close()
        log.info("Close bridge")

