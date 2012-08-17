#!/usr/bin/env python
"""
Test cases for oan.node_manager.commands

"""

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import mock

from uuid import UUID
from datetime import datetime, timedelta

from oan import manager
from oan.config import OANConfig
from oan.manager import node_manager
from oan.async.network_node import OANNetworkNode
from oan.node_manager.node_manager import OANNodeManager
from test.test_case import OANTestCase
from oan.heartbeat import OANHeartbeat
from oan.dispatcher.message import OANMessageHeartbeat
from oan.node_manager.command import (OANCommandStaticHeartbeat,
                                      OANCommandCleanOutQueue,
                                      OANCommandStaticSyncNodes)


class TestOANNodeManagerCommands(OANTestCase):

    _mock_database = None
    _mock_network = None
    _mock_dispatcher = None

    def setUp(self):
        self._mock_database = mock.MagicMock()
        self._mock_database.shutdown.return_value = True

        self._mock_network = mock.MagicMock()
        self._mock_network.shutdown.return_value = True
        self._mock_network.execute.return_value = None

        self._mock_dispatcher = mock.MagicMock()
        self._mock_dispatcher.shutdown.return_value = True
        self._mock_dispatcher.execute.return_value = None


        config = OANConfig(
            "00000000-0000-aaaa-0000-000000000000",
            "TestOANNodeManager",
            "localhost",
            str(9000)
        )

        mock_shutdown = mock.Mock()
        mock_shutdown.shutdown.return_value = True

        manager.setup(
            mock_shutdown,
            mock_shutdown,
            OANNodeManager(config),
            self._mock_database,
            self._mock_dispatcher,
            self._mock_network
        )

        #load also sets my node in node_manager.
        self._mock_database.select_all.return_value.__iter__.return_value = \
            iter(self.create_nodes())

        node_manager().load()

    def tearDown(self):
        manager.shutdown()
        self._mock_database = None

    def create_node(self, port, minute_delta):
        node = OANNetworkNode.create(
            UUID('00000000-0000-aaaa-%s-000000000000' % port),
            'localhost', port, False)

        date_fmt = "%Y-%m-%dT%H:%M:%SZ"
        date_value = (datetime.utcnow() + timedelta(minutes = minute_delta))
        heartbeat_value = date_value.strftime(date_fmt)
        node.update(heartbeat = heartbeat_value)

        return node

    def create_nodes(self):
        """ creates test nodes with diffrent heartbeat values """
        ret = []
        ret.append(self.create_node(8000, -OANHeartbeat.DEAD_MIN))
        ret.append(self.create_node(8001, -OANHeartbeat.OFFLINE_MIN))
        ret.append(self.create_node(8002, -OANHeartbeat.EXPIRED_MIN))
        ret.append(self.create_node(8003, -OANHeartbeat.IDLE_MIN))
        ret.append(self.create_node(8004, 0))
        return ret

    def test_command_heartbeat_not_blocked(self):
        OANCommandStaticHeartbeat.execute()
        for node in node_manager().get_nodes():
            if (not node.has_heartbeat_state(OANHeartbeat.DEAD) and
                node.has_heartbeat_state(OANHeartbeat.EXPIRED)):
                self.assertTrue(node.out_queue.qsize() > 0)

    def test_command_heartbeat_blocked(self):
        my_node = node_manager().get_my_node()
        my_node.update(blocked = True)

        OANCommandStaticHeartbeat.execute()
        for node in node_manager().get_nodes():
            if (not node.has_heartbeat_state(OANHeartbeat.DEAD)):
                self.assertTrue(node.out_queue.qsize() > 0)

    def test_command_clean_out_queue(self):
        node = node_manager().get_node(UUID("00000000-0000-aaaa-8002-000000000000"))
        clean_message = OANCommandCleanOutQueue.create(node)
        for x in xrange(0,10):
            node.send(OANMessageHeartbeat.create())

        self.assertEqual(node.out_queue.qsize(), 10)
        clean_message.execute()
        self.assertEqual(node.out_queue.qsize(), 0)

    def test_command_node_sync(self):
        OANCommandStaticSyncNodes.execute()
        for node in node_manager().get_nodes():
            if (node.has_heartbeat_state(OANHeartbeat.NOT_OFFLINE)):
                self.assertTrue(node.out_queue.qsize() > 0)



