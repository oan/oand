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

from test.test_case import OANTestCase
from oan.util import log
from oan.util.daemon_base import OANDaemonBase
from oan.util.signal_handler import OANTerminateInterrupt
from oan.network.server import OANListen
from oan.network.bridge import OANBridge, OANBridgeAuth
from oan.network import serializer

def start_asyncore_loop(timeout, name = "asynco"):
    def run(timeout):
        log.info("Start asyncore loop")
        asyncore.loop(timeout = timeout, use_poll = True)
        log.info("Stop asyncore loop")

    t = Thread(target=run, kwargs={
        'timeout' : timeout})
    t.name=name
    t.start()

class MessageTest():
    def __init__(self, text = None):
        self.status = "ok"
        self.text = text


class ServerNodeDaemon(OANDaemonBase):
    def run(self):
        try:
            serializer.add(MessageTest)
            auth = OANBridgeAuth.create(
                'oand v1.0', '00000000-0000-code-1338-000000000000',
                'localhost', 1338, False
            )
            listen = OANListen(auth)
            listen.accept_callback = self.accept
            listen.start()
            start_asyncore_loop(60)
            self.wait()

        except OANTerminateInterrupt:
            pass

    def accept(self, bridge):
        log.info("ServerNodeDaemon::accept")
        bridge.message_callback = self.received

    def received(self, bridge, message):
        log.info("ServerNodeDaemon::received")
        if message.__class__.__name__ == 'MessageTest':
            bridge.send([MessageTest(message.text)])


class TestOANBridge(OANTestCase):
    # Remote node to test network against.
    daemon = None

    # Callback counters
    connect_counter = None
    message_counter = None
    close_counter = None

    def setUp(self):
        serializer.add(MessageTest)

        self.daemon = ServerNodeDaemon(
            pidfile="/tmp/ut_daemon.pid", stdout='/tmp/ut_out.log',
            stderr='/tmp/ut_err.log')
        self.daemon.start()
        self.connect_counter = 0
        self.message_counter = 0
        self.close_counter = 0
        self._auth = OANBridgeAuth.create(
            'oand v1.0', '00000000-0000-code-1337-000000000000', 'localhost',
            1337, False)

    def tearDown(self):
        self.daemon.stop()

    def connect_cb(self, bridge, auth):
        self.connect_counter += 1

    def message_cb(self, bridge, message):
        if isinstance(message, MessageTest):
            self.message_counter += 1

    def close_cb(self, bridge):
        self.close_counter += 1

    def test_bridge(self):
        bridge = OANBridge("localhost", 1338, self._auth)
        self.assertTrue(bridge.readable())
        self.assertFalse(bridge.writable())

        bridge.connect_callback = self.connect_cb
        bridge.message_callback = self.message_cb
        bridge.close_callback = self.close_cb
        bridge.send([MessageTest("Hello world")])
        self.assertTrue(bridge.readable())
        self.assertTrue(bridge.writable())

        bridge.connect()
        start_asyncore_loop(1)

        log.info(bridge.connected)
        log.info(self.connect_counter)
        log.info(self.message_counter)

        self.assertTrueWait(lambda : bridge.connected)
        self.assertTrueWait(lambda : self.connect_counter == 1)
        self.assertTrueWait(lambda : self.message_counter == 1)

        bridge.shutdown()
        self.assertTrueWait(lambda : self.close_counter == 1)
        self.assertTrueWait(lambda : bridge.connected == False)
        self.assertFalse(bridge.writable())

    def disabled_test_two_asyncoreloops(self):
        """
        Test that two asyncore loops can be started after each other in the
        same main thread.

        """
        bridge = OANBridge("localhost", 1338, self._auth)
        bridge.send([MessageTest("Hello world")])
        self.assertTrue(bridge.readable())
        self.assertTrue(bridge.writable())

        bridge.connect()

        start_asyncore_loop(4, name="async2")

        self.assertTrueWait(lambda : bridge.connected)
        self.assertTrueWait(lambda : bridge.connected == False)
        self.assertFalse(bridge.writable())


