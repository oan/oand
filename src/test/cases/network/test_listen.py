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
from oan.network.server import OANListen
from oan.network.bridge import OANBridge, OANBridgeAuth
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


class ClientNodeDaemon(OANDaemonBase):
    close_done = None
    def run(self):
        self.close_done = False
        serializer.add(MessageTest)

        auth = OANBridgeAuth.create(
            'oand v1.0', '00000000-0000-code-1338-000000000000',
            'localhost', 1338, False
        )

        bridge = OANBridge("localhost", 1337, auth)
        bridge.out_queue = Queue()
        bridge.out_queue.put(MessageTest("Hello world"))
        bridge.connect()
        bridge.message_callback = self.message_cb
        bridge.close_callback = self.close_cb
        start_asyncore_loop()
        while not self.close_done:
            pass

        log.info("ClientNodeDaemon:run end")

    def message_cb(self, bridge, message):
         if message.__class__.__name__ == 'MessageTest':
            bridge.shutdown()

    def close_cb(self, bridge):
        log.info("ClientNodeDaemon:close_cb")
        self.close_done = True


class TestOANListen(OANTestCase):
    # Remote node to test network against.
    daemon = None

    # Callback counters
    accept_counter = None
    connect_counter = None
    message_counter = None
    close_counter = None

    def setUp(self):
        serializer.add(MessageTest)

        self.daemon = ClientNodeDaemon(
            pidfile="/tmp/ut_daemon.pid", stdout='/tmp/ut_out.log',
            stderr='/tmp/ut_err.log')
        self.accept_counter = 0
        self.connect_counter = 0
        self.message_counter = 0
        self.close_counter = 0

        self._auth = OANBridgeAuth.create(
            'oand v1.0', '00000000-0000-code-1337-000000000000', 'localhost',
            1337, False)


    def tearDown(self):
        self.daemon.stop()

    def accept_cb(self, bridge):
        log.info("TestOANListen::accept")
        bridge.out_queue = Queue()
        bridge.connect_callback = self.connect_cb
        bridge.message_callback = self.message_cb
        bridge.close_callback = self.close_cb

    def connect_cb(self, bridge, auth):
        self.connect_counter += 1

    def message_cb(self, bridge, message):
        if message.__class__.__name__ == 'MessageTest':
            self.message_counter += 1
            bridge.out_queue.put(MessageTest(message.text))

    def close_cb(self, bridge):
        self.close_counter += 1

    def test_bridge(self):
        listen = OANListen(self._auth)
        listen.accept_callback = self.accept_cb
        listen.start()
        start_asyncore_loop()

        self.daemon.start()
        self.assertTrueWait(lambda : self.message_counter == 1)
        self.assertTrueWait(lambda : self.close_counter == 1)
        self.assertTrueWait(lambda : self.connect_counter == 1)

        log.info("Close bridge")

