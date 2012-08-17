#!/usr/bin/env python
"""
Test cases for oan.async.bridge

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
from time import sleep
from collections import deque

from test.test_case import OANTestCase
from oan.util import log
from oan.util.daemon_base import OANDaemonBase
from oan.util.signal_handler import OANSignalHandler, OANTerminateInterrupt
from oan.async.server import OANListen
from oan.async.bridge import OANBridge
from oan.async import serializer


def start_asyncore_loop(timeout, name = "asynco"):
    def run(timeout):
        log.info("Start asyncore loop")
        asyncore.loop(timeout = timeout, use_poll = True)
        log.info("Stop asyncore loop")

    t = Thread(target=run, kwargs={
        'timeout' : timeout})

    t.name=name
    t.daemon = True
    t.start()


class MessageTest():
    def __init__(self, text = None):
        self.status = "ok"
        self.text = text


class ServerNodeDaemon(OANDaemonBase):
    _auth = None

    _nodes = []

    _connected_bridges = []

    _concurrent_bridges = 10

    def __init__(self, auth, nodes):
        self._auth = auth
        self._nodes = deque(nodes)

    def run(self):
        serializer.add(MessageTest)
        listen = OANListen(self._auth)
        listen.accept_callback = self.accept
        listen.start()

        while True:
            try:
                OANSignalHandler.activate()
                asyncore.loop(timeout = 60, use_poll = True)
                OANSignalHandler.deactivate()
                sleep(5)
                self.send_heartbeat(self)

            except OANTerminateInterrupt:
                break

    def send_heartbeat(self):
        while len(self._connected_bridges) < self._concurrent_bridges:
            node_auth = self._nodes.popleft()
            bridge = OANBridge(node_auth.host, node_auth.port, self._auth)
            self._connected_bridges.append(bridge)

    def bridge_accept(self, bridge):
        log.info("ServerNodeDaemon::accept")
        bridge.connect_callback = self.connected
        bridge.message_callback = self.message

    def bridge_message(self, bridge, message):
        log.info("ServerNodeDaemon::message")


class TestOANBridge(OANTestCase):
    # Remote node to test network against.
    daemon = None

    # Callback counters
    received_counter = None
    close_counter = None

    # Set by error_cb
    last_error = None

    def setUp(self):
        serializer.add(MessageTest)

        self.daemon = ServerNodeDaemon(
            "/tmp/oand_ut_daemon.pid", stdout='/tmp/ut_out.log',
            stderr='/tmp/ut_err.log')
        self.received_counter = 0
        self.close_counter = 0
        self.last_error = None

    def received_cb(self, bridge, message):
        if message.text == "Hello world":
            self.received_counter += 1
            log.info("received_counter [%s]" % self.received_counter)

    def close_cb(self, bridge):
        self.close_counter += 1

    def error_cb(self, bridge, exc_type, exc_value):
        self.last_error = str(exc_value)

    def test_bridge(self):
        """Should be stopped before all messages has been echoed back"""
        self.daemon.start()
        bridge = OANBridge()
        bridge.out_queue = Queue()
        bridge.received_callback = self.received_cb
        bridge.close_callback = self.close_cb
        bridge.connect("localhost", 1338)
        start_asyncore_loop(0.1)

        for x in xrange(1, 300):
            bridge.out_queue.put(MessageTest("Hello world"))

        bridge.shutdown()

        self.assertTrueWait(lambda : self.close_counter == 1)
        self.assertTrueWait(lambda : self.received_counter < 300)
        self.daemon.stop()

    def test_remote_is_gone(self):
        """Test that bridge can handle lost connection to remote node."""
        bridge = OANBridge()
        bridge.out_queue = Queue()
        bridge.error_callback = self.error_cb
        bridge.out_queue.put(MessageTest("Hello world"))
        bridge.connect("localhost", 1338)
        start_asyncore_loop(0.1)

        self.assertTrueWait(lambda : self.last_error == "[Errno 61] Connection refused")
