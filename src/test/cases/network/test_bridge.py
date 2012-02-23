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

import mock
from uuid import UUID
from time import sleep
import sys
import socket
import asyncore

from test.test_case import OANTestCase

from oan import manager
from oan.manager import network
from oan.util import log
from oan.util.daemon_base import OANDaemonBase, OANSigtermError

from oan.network.network import OANNetwork
from oan.network.bridge import OANBridge
from oan.network.network_node import OANNetworkNode
from oan.network.command import OANNetworkCommandListen


# Files used in test.
F_PID="/tmp/oand_ut_daemon.pid"
F_OUT="/tmp/oand_ut_daemon.out"
F_ERR="/tmp/oand_ut_daemon.err"
F_SERVER_LOG="/tmp/oand_ut_server.log"
F_CLIENT_LOG="/tmp/oand_ut_client.log"


def setup_managers(port, logfile):

    class mock_shutdown(mock.Mock):
        def shutdown(self): return True

    class mock_dispatcher(mock_shutdown):
        pass

    class mock_nodemanager(mock_shutdown):
        def get_my_node(self):
            return OANNetworkNode.create(
                UUID("00000000-0000-0000-%s-000000000000" % port),
                "192.168.0.10",
                port,
                False
            )

        def create_node(self, oan_id, host, port, blocked):
            return OANNetworkNode.create(oan_id, host, port, blocked)

    manager.setup(
        OANNetwork(),
        mock_shutdown(),
        mock_dispatcher(),
        mock_shutdown(),
        mock_shutdown(),
        mock_nodemanager()
    )

    log.setup(
        log.NONE,
        log.NONE,
        log.DEBUG, logfile
    )


def shutdown_managers():
    log.info("Stop managers")
    manager.shutdown()
    log.info("-----------------------------------------")


class ServerNodeDaemon(OANDaemonBase):

    def run(self):
        try:
            setup_managers(1338, F_SERVER_LOG)
            network().execute(OANNetworkCommandListen.create(1338))

            while True:
                pass
        except OANSigtermError:
            pass
        finally:
            shutdown_managers()
            pass

class MockServer(object):
    bridges = None
    def __init__(self):
        self.bridges = []

    def add_bridge(self, bridge):
        self.bridges.append(bridge)

    def remove_bridge(self, bridge):
        self.bridges.remove(bridge)


class OANTestBridge(OANBridge):
    last_error = None
    def handle_error(self):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        if exc_type == socket.error and exc_value.errno == 61:
            self.last_error = exc_value.errno

        OANBridge.handle_error(self)


class TestOANBridge(OANTestCase):
    # Remote node to test network against.
    daemon = None

    @classmethod
    def setUpClass(cls):
        # Truncate all log files
        open(F_OUT, "w").close()
        open(F_ERR, "w").close()
        open(F_SERVER_LOG, "w").close()
        open(F_CLIENT_LOG, "w").close()

    def setUp(self):
        self.server = MockServer()

    # def test_network(self):
    #     setup_managers(1337, F_CLIENT_LOG)

    #     log.debug("Bridge start")

    #     bridge = OANTestBridge(self.server)
    #     bridge.connect("localhost", 1338)
    #     sleep(1)
    #     log.debug("loop start")
    #     asyncore.loop()
    #     log.debug("loop end")

    #     self.assertFalse(bridge.connected)
    #     self.assertEqual(len(self.server.bridges), 0)

    #     log.debug("Bridge stop")
    #     shutdown_managers()

    def test_network_daemon(self):
        self.daemon = ServerNodeDaemon(F_PID, stdout=F_OUT, stderr=F_ERR)
        self.daemon.start()
        sleep(1)

        # Test if server node started.
        self.assertTrue(self.daemon.is_alive())

        self.network_daemon_test()

        self.daemon.stop()

    def network_daemon_test(self):

        setup_managers(1337, F_CLIENT_LOG)
        sleep(2)

        log.debug("Bridge start")

        bridge = OANTestBridge(self.server)
        bridge.connect("localhost", 1338)
        sleep(1)
        log.debug("loop start")
        asyncore.loop()
        log.debug("loop end")

        # self.assertTrue(bridge.connected)
        # self.assertEqual(len(self.server.bridges), 1)

        log.debug("Bridge stop")
        shutdown_managers()
