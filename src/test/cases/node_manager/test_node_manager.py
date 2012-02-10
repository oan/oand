#!/usr/bin/env python
"""
Test cases for oan.node_manager.node_manager.node_manager

"""

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import mock
import Queue

from uuid import UUID
from datetime import datetime, timedelta

from oan import manager
from oan.manager import dispatcher, node_manager
from oan.config import OANConfig
from oan.network.network_node import OANNetworkNode
from oan.node_manager.node_manager import OANNodeManager
from test.test_case import OANTestCase
from oan.heartbeat import OANHeartbeat
from oan.node_manager.command import OANCommandStaticHeartbeat


class OANTestMessageSelect:
    """A test message to yield many values from a message."""
    def execute(self):
        for i in xrange(10):
            yield "My select [%d]" % i


class OANTestMessageYield:
    """A simple test message to return one value."""
    def execute(self):
        return "My return value"


class OANTestMessageStatic:
    """
    A static test message that will be put in the dispatcher
    without a instance.

    """

    @staticmethod
    def execute():
        return "My return from static message"


class TestOANNodeManager(OANTestCase):

    _mock_database = None
    _mock_network = None

    def setUp(self):
        self._mock_database = mock.MagicMock()
        self._mock_database.shutdown.return_value = True

        self._mock_network = mock.MagicMock()
        self._mock_network.shutdown.return_value = True
        self._mock_network.execute.return_value = None

        config = OANConfig(
            "00000000-0000-aaaa-0000-000000000000",
            "TestOANNodeManager",
            "localhost",
            str(9000)
        )

        mock_shutdown = mock.Mock()
        mock_shutdown.shutdown.return_value = True

        manager.setup(
            self._mock_network,
            self._mock_database,
            mock_shutdown,
            mock_shutdown,
            mock_shutdown,
            OANNodeManager(config)
        )

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

    def test_load(self):
        test_nodes = self.create_nodes()

        self._mock_database.select_all.return_value.__iter__.return_value = \
            iter(test_nodes)

        node_manager().load()
        nodes = node_manager().get_nodes()

        for n in test_nodes:
            self.assertTrue(n in nodes)

        for n in nodes:
            self.assertTrue(n in test_nodes)

    def test_get_my_node(self):

        #before load my node should be None
        n1 = node_manager().get_my_node()
        self.assertEqual(n1, None)

        #load also sets my node in node_manager.
        self._mock_database.select_all.return_value.__iter__.return_value = \
            iter([])

        node_manager().load()

        n1 = node_manager().get_my_node()
        self.assertTrue(n1 is not None)

        (name, host, port, blocked, state, heartbeat) = n1.get()

        self.assertEqual(n1.oan_id,
            UUID('00000000-0000-aaaa-0000-000000000000'))

        self.assertEqual(host, "localhost")
        self.assertEqual(port, 9000)
        self.assertEqual(blocked, False)


    def test_create_node(self):
        # create the node with node_manager
        n1 = node_manager().create_node(
            UUID('00000000-0000-bbbb-4008-000000000000'),
            'localhost', 4000, False)

        (name, host, port, blocked, state, heartbeat) = n1.get()

        self.assertEqual(n1.oan_id,
            UUID('00000000-0000-bbbb-4008-000000000000'))

        self.assertEqual(host, "localhost")
        self.assertEqual(port, 4000)
        self.assertEqual(blocked, False)

        # if the node already exist update the info on that node.
        n2 = node_manager().create_node(
            UUID('00000000-0000-bbbb-4008-000000000000'),
            'my_host', 4001, True)

        (name, host, port, blocked, state, heartbeat) = n2.get()
        self.assertEqual(host, 'my_host')
        self.assertEqual(port, 4001)
        self.assertEqual(blocked, True)

        # the info should be updated on all references
        (name, host, port, blocked, state, heartbeat) = n1.get()
        self.assertEqual(host, 'my_host')
        self.assertEqual(port, 4001)
        self.assertEqual(blocked, True)

    def test_exist_node(self):
        node_manager().create_node(
            UUID('00000000-0000-bbbb-4008-000000000000'),
            'localhost', 4000, False)

        self.assertTrue(node_manager().exist_node(UUID('00000000-0000-bbbb-4008-000000000000')))

    def test_get_node(self):
        n1 = node_manager().create_node(
            UUID('00000000-0000-bbbb-4008-000000000000'),
            'localhost', 4000, False)

        # get the node from node_manager to ensure that the node
        # is added to node_manager
        n2 = node_manager().get_node(
            UUID('00000000-0000-bbbb-4008-000000000000'))

        self.assertEqual(n1, n2)

    def test_get_nodes(self):
        test_nodes = self.create_nodes()

        self._mock_database.select_all.return_value.__iter__.return_value = \
            iter(test_nodes)

        node_manager().load()

        self.assertEqual(len(node_manager().get_nodes(OANHeartbeat.IDLE)), 4)
        self.assertEqual(len(node_manager().get_nodes(OANHeartbeat.NOT_IDLE)), 1)

        self.assertEqual(len(node_manager().get_nodes(OANHeartbeat.EXPIRED)), 3)
        self.assertEqual(len(node_manager().get_nodes(OANHeartbeat.NOT_EXPIRED)), 2)

        self.assertEqual(len(node_manager().get_nodes(OANHeartbeat.OFFLINE)), 2)
        self.assertEqual(len(node_manager().get_nodes(OANHeartbeat.NOT_OFFLINE)), 3)

        self.assertEqual(len(node_manager().get_nodes(OANHeartbeat.DEAD)), 1)
        self.assertEqual(len(node_manager().get_nodes(OANHeartbeat.NOT_DEAD)), 4)

    def test_send(self):
        n1 = node_manager().create_node(
            UUID('00000000-0000-bbbb-4008-000000000000'),
            'localhost', 4000, False)

        node_manager().send(n1.oan_id, OANCommandStaticHeartbeat)
        self.assertEqual(n1.out_queue.get(), OANCommandStaticHeartbeat)


    def test_relay_node(self):
        pass

    def test_queue_full(self):
        n1 = node_manager().create_node(
            UUID('00000000-0000-bbbb-4008-000000000000'),
            'localhost', 4000, False)

        with self.assertRaises(Queue.Full):
            for x in xrange(2000):
                node_manager().send(n1.oan_id, OANCommandStaticHeartbeat)


