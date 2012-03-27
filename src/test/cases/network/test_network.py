#!/usr/bin/env python
"""
Test cases for oan.network.network

"""

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import asyncore
from threading import Thread
from uuid import UUID

from test.test_case import OANTestCase
from oan.util import log
from oan.util.daemon_base import OANDaemonBase
from oan.util.signal_handler import OANTerminateInterrupt
from oan.network.bridge import OANBridgeAuth
from oan.network.network import OANNetworkServer
from oan.network.node_manager import OANNodeManager
from oan.network import serializer
from oan.config import OANConfig


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


# Message counters
to_client_counter = 0


class MessageTestToServer():
    def __init__(self, text = None):
        self.status = "ok"
        self.text = text

    def execute(self):
        MessageTestToClient(self.text)


class MessageTestToClient():
    def __init__(self, text = None):
        self.status = "ok"
        self.text = text

    def execute(self):
        global to_client_counter
        to_client_counter += 1


class ServerNodeDaemon(OANDaemonBase):
    def run(self):
        try:
            serializer.add(MessageTestToServer)
            serializer.add(MessageTestToClient)
            auth = OANBridgeAuth.create(
                'oand v1.0', UUID('00000000-0000-c0de-1338-000000000000'),
                'localhost', 1338, False
            )
            OANNetworkServer.init(auth)
            OANNetworkServer.listen()
            start_asyncore_loop(60)

            self.wait()
            log.info("end")

        except OANTerminateInterrupt:
            log.info("Interupt")
            pass
        log.info("Exit runt")


class TestOANBridge(OANTestCase):
    # Remote node to test network against.
    daemon = None

    def setUp(self):
        global to_client_counter
        to_client_counter = 0

        serializer.add(MessageTestToServer)
        serializer.add(MessageTestToClient)

        self.daemon = ServerNodeDaemon(
            pidfile="/tmp/ut_daemon.pid", stdout='/tmp/ut_out.log',
            stderr='/tmp/ut_err.log')
        self.daemon.start()

        self._auth = OANBridgeAuth.create(
            'oand v1.0', UUID('00000000-0000-c0de-1337-000000000000'), 'localhost',
            1337, False)

        self._config = OANConfig(
            '00000000-0000-c0de-1337-000000000000',
            "c0de-1337",
            'localhost',
            "1337",
            "localhost",
            "1338",
            False
        )
        OANNodeManager.init(self._config)
        OANNodeManager.load()

    def tearDown(self):
        log.info('tearDown')
        self.daemon.stop()

    def test_bridge(self):
        OANNodeManager.create_node(
            UUID('00000000-0000-c0de-1338-000000000000'), 'localhost', 1338, False
        )
        OANNetworkServer.init(self._auth)
        OANNetworkServer.connect()
        start_asyncore_loop(1)
        self.assertTrueWait(lambda : len(OANNetworkServer._bridges) == 1)
        #OANNetworkServer.send(MessageTestToServer("Hello World"))

        #self.assertTrueWait(lambda : to_client_counter == 1)
        log.info("Stop it")

