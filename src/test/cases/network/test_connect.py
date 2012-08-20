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

from test.test_case import OANTestCase
from oan.util import log
from oan.util.daemon_base import OANDaemonBase
from oan.util.signal_handler import OANTerminateInterrupt
from oan.network import serializer
from oan.network.server import OANServer, OANAuth

class MessageTest():
    def __init__(self, text = None):
        self.status = "ok"
        self.text = text

class ServerNodeDaemon(OANDaemonBase):
    def run(self):
        try:
            serializer.add(MessageTest)
            auth = OANAuth(
                'oand v1.0', '00000000-0000-code-1338-000000000000',
                'localhost', 1338, False
            )

            OANServer.connect_callback = self.connect_cb
            OANServer.message_callback = self.message_cb
            OANServer.start(auth)
            self.wait()

        except OANTerminateInterrupt:
            OANServer.shutdown()

    def connect_cb(self, auth):
        log.info("ServerNodeDaemon::connect")

    def message_cb(self, url, messages):
        log.info("ServerNodeDaemon::message")
        OANServer.push([url], messages)

class TestOANConnect(OANTestCase):
    # Remote node to test network against.
    daemon = None

    def setUp(self):
        self.reset_all_counters()
        serializer.add(MessageTest)

        self.daemon = ServerNodeDaemon(
            pidfile="/tmp/ut_daemon.pid", stdout='/tmp/ut_out.log',
            stderr='/tmp/ut_err.log')
        self.daemon.start()
        self._auth = OANAuth(
            'oand v1.0', '00000000-0000-code-1337-000000000000', 'localhost',
            1337, False)

    def tearDown(self):
        self.daemon.stop()

    def connect_cb(self, auth):
        self.inc_counter("connects")

    def message_cb(self, auth, messages):
        self.inc_counter("messages", len(messages))

    def close_cb(self, auth):
        self.inc_counter("closes")

    def test_connect(self):
        OANServer.connect_callback = self.connect_cb
        OANServer.message_callback = self.message_cb
        OANServer.close_callback = self.close_cb

        OANServer.start(self._auth)
        OANServer.push([("localhost", 1338)], [serializer.encode(MessageTest("Hello world"))])

        self.assert_counter_wait('connects', 1)
        self.assert_counter_wait('messages', 1)

        OANServer.shutdown()

        self.assert_counter_wait('closes', 1)
