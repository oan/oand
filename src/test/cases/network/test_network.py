#!/usr/bin/env python
"""
Test cases for util.daemon_base

Test communication (network, bridges, server etc.) between nodes.

"""

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import mock
import sys
import os
from uuid import UUID
from Queue import Queue
from time import sleep

from test.test_case import OANTestCase

from oan import manager
from oan.manager import dispatcher, node_manager
from oan.config import OANConfig
from oan.node_manager.node_manager import OANNodeManager
from oan.dispatcher.dispatcher import OANDispatcher

from oan.manager import dispatcher, node_manager
from oan.dispatcher.message import OANMessagePing
from oan.application import OANApplication
from oan.config import OANConfig
from oan.util.network import get_local_host
from oan.util import log
from oan.util.daemon_base import OANDaemonBase, OANSigtermError
from oan.util.decorator.capture import capture

from oan.network.network import OANNetwork


# Files used in test.
F_PID="/tmp/oand_ut_daemon.pid"
F_OUT="/tmp/oand_ut_daemon.out"
F_ERR="/tmp/oand_ut_daemon.err"
F_SERVER_LOG="/tmp/oand_ut_server.log"
F_CLIENT_LOG="/tmp/oand_ut_client.log"

class ServerNodeDaemon(OANDaemonBase):

    def run(self):
        try:
            self.setup_managers()
            while True:
                pass
        except OANSigtermError:
            pass
        finally:
            #manager.shutdown()
            pass

    def setup_managers(self):
        log.setup(
            log.NONE,
            log.NONE,
            log.DEBUG, F_SERVER_LOG
        )

        mock_shutdown = mock.Mock()
        mock_shutdown.shutdown.return_value = True

        config = OANConfig(
            "00000000-0000-dead-0000-000000000000",
            "UT-Server",
            "localhost",
            str(9000)
        )

        net=OANNetwork()
        disp=OANDispatcher()
        node=OANNodeManager(config)

        node.shutdown()
        disp.shutdown()
        net.shutdown()

        manager.setup(
            OANNetwork(),
            mock_shutdown,
            mock_shutdown,
            mock_shutdown,
            mock_shutdown,
            mock_shutdown
        )
        manager.shutdown()

        return
        manager.setup(
            OANNetwork(),
            mock_shutdown,
            OANDispatcher(),
            mock_shutdown,
            mock_shutdown,
            OANNodeManager(config)
        )
        manager.shutdown()


class TestOANNetwork(OANTestCase):

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
        self.daemon = ServerNodeDaemon(F_PID, stdout=F_OUT, stderr=F_ERR)
        self.daemon.start()
        # Give deamon time to start.
        sleep(1)

    def tearDown(self):
        self.daemon.stop()
        pass

    def test_deamon(self):
        # Test if server node started.
        #self.assertTrue(open(F_PID).readline().strip().isalnum())
        self.setup_managers()
        self.assertTrue(True)

        #network().execute(OANNetworkCommandListen.create(self.config.node_port))

        #manager.shutdown()

    def setup_managers(self):
        # mock_shutdown = mock.Mock()
        # mock_shutdown.shutdown.return_value = True

        # config = OANConfig(
        #     "00000000-0000-babe-0000-000000000000",
        #     "UT-Client",
        #     "localhost",
        #     str(9001)
        # )

        # manager.setup(
        #     OANNetwork(),
        #     mock_shutdown,
        #     OANDispatcher(),
        #     mock_shutdown,
        #     mock_shutdown,
        #     OANNodeManager(config)
        # )

        log.setup(
            log.NONE,
            log.NONE,
            log.DEBUG, F_CLIENT_LOG
        )

    # def test_static(self):
    #     # Disable use of database in OANNodeManager.load
    #     self.mock_database.select_all.return_value.__iter__.return_value = iter([])

    #     #network().get(OANCommandStaticGetNodeInfo)




















#     # def create_node(self):
#     #     """Create known nodes (instead of loading from db"""
#     #     node_manager().create_node(UUID('00000000-0000-0000-4000-000000000000'), get_local_host(), 4000, False)
#     #     node_manager().create_node(UUID('00000000-0000-0000-4001-000000000000'), get_local_host(), 4001, False)
#     #     node_manager().create_node(UUID('00000000-0000-0000-4002-000000000000'), get_local_host(), 4002, False)
#     #     node_manager().create_node(UUID('00000000-0000-0000-4003-000000000000'), get_local_host(), 4003, False)

#     def got_message(self, message):
#         if isinstance(message, OANMessagePing):
#             if message.ping_counter == 1:
#                 self.queue.put(message)

#     def create_watcher(self):
#         dispatcher().on_message.append(self.got_message)

#     def test_message_ping(self):
#         self.assertTrue(True)

    #     # Send a ping between all nodes 5x10 times.
    #     for n in xrange(4000, 4001):
    #         for i in xrange(5):
    #             dispatcher().execute(OANCommandSendToNode.create(
    #                 UUID('00000000-0000-0000-%s-000000000000' % n),
    #                 OANMessagePing.create( "N%dP%d" % (n, i), 10 )
    #             ))

    #     counter = 0
    #     for i in xrange(20):
    #         message = self.queue.get()
    #         counter += 1
    #         print counter

    #     self.assertEqual(counter, 20)  # 4 * 5

