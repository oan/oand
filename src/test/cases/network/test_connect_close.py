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

from time import sleep

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
        for message in messages:
            OANServer.push([url], [message])
            sleep(0.0001)


class TestOANConnectClose(OANTestCase):
    # Remote node to test network against.
    daemon = None

    # Callback counters
    received_counter = None
    close_counter = None

    # Set by error_cb
    last_error = None

    _auth = None

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

    def error_cb(self, auth, messages):
        self.inc_counter("errors")

    def test_shutdown_when_sending(self):
        """Should be stopped before all messages has been echoed back"""
        OANServer.connect_callback = self.connect_cb
        OANServer.message_callback = self.message_cb
        OANServer.close_callback = self.close_cb

        OANServer.start(self._auth)

        log.info(self.assert_counters)
        mess = serializer.encode(MessageTest("Hello world"))
        messages = []
        for x in xrange(0, 500):
            messages.append(mess)

        OANServer.push([("localhost", 1338)], messages)
        sleep(0.1)
        OANServer.shutdown()

        self.assert_counter_wait('connects', 1)
        self.assert_counter_wait('closes', 1)
        self.assert_counter_less('messages', 500)

    def test_remote_is_gone(self):
        """Test that error is called when pushing to non existing url."""

        OANServer.error_callback = self.error_cb
        OANServer.start(self._auth)
        OANServer.push([("localhost", 1700)], [serializer.encode(MessageTest("Hello world"))])

        self.assert_counter_wait('errors', 1)
        OANServer.shutdown()
