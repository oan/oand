#!/usr/bin/env python
"""
Test cases for oan.async.network_node.py

"""

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from uuid import UUID
from test.test_case import OANTestCase

from oan.async.network_node import OANNetworkNode, OANNetworkNodeState
from oan.heartbeat import OANHeartbeat

class TestOANNetworkNode(OANTestCase):
    def test_network_node_invalid_uuid(self):
        with self.assertRaises(TypeError):
            OANNetworkNode("invalid-id")

    def test_network_node_empty(self):
        nn = OANNetworkNode(UUID("00000000-0000-dead-0000-000000000000"))

        (name, host, port, blocked, state, heartbeat) = nn.get()

        self.assertTrue(nn.out_queue.empty())
        self.assertEqual(str(nn.oan_id), "00000000-0000-dead-0000-000000000000")
        self.assertEqual(host, None)
        self.assertEqual(port, None)
        self.assertEqual(blocked, None)
        self.assertEqual(state, OANNetworkNodeState.DISCONNECTED)
        self.assertTrue(nn.is_disconnected())
        self.assertTrue(nn.has_heartbeat_state(OANHeartbeat.OFFLINE))

    def test_network_node_create(self):
        nn = OANNetworkNode.create(
            UUID("00000000-0000-dead-0000-000000000000"),
            "localhost", 1337, False
        )

        (name, host, port, blocked, state, heartbeat) = nn.get()

        self.assertTrue(nn.out_queue.empty())
        self.assertEqual(str(nn.oan_id), "00000000-0000-dead-0000-000000000000")
        self.assertEqual(host, "localhost")
        self.assertEqual(port, 1337)
        self.assertEqual(blocked, False)
        self.assertEqual(state, OANNetworkNodeState.DISCONNECTED)
        self.assertTrue(nn.is_disconnected())
        self.assertTrue(nn.has_heartbeat_state(OANHeartbeat.OFFLINE))

    def test_network_node_update(self):
        nn = OANNetworkNode.create(
            UUID("00000000-0000-dead-0000-000000000000"),
            "localhost", 1337, False
        )

        nn.update(
            "your-node", "remotehost", 1338,
            True, OANNetworkNodeState.CONNECTING,
            "2107-07-07T07:07:07Z"
        )

        (name, host, port, blocked, state, heartbeat) = nn.get()

        self.assertTrue(nn.out_queue.empty())
        self.assertEqual(str(nn.oan_id), "00000000-0000-dead-0000-000000000000")
        self.assertEqual(host, "remotehost")
        self.assertEqual(port, 1338)
        self.assertEqual(blocked, True)
        self.assertEqual(state, OANNetworkNodeState.CONNECTING)
        self.assertFalse(nn.is_disconnected())
        self.assertFalse(nn.has_heartbeat_state(OANHeartbeat.OFFLINE))

    def test_network_node_serialize(self):
        nn = OANNetworkNode.create(
            UUID("00000000-0000-dead-0000-000000000000"),
            "localhost", 1337, False
        )

        nn.update(
            "your-node", "remotehost", 1338,
            True, OANNetworkNodeState.CONNECTING,
            "2107-07-07T07:07:07Z"
        )
        data = nn.serialize()

        nn2 = OANNetworkNode(UUID("00000000-0000-babe-0000-000000000000"))
        nn2.unserialize(data)

        (name, host, port, blocked, state, heartbeat) = nn2.get()

        self.assertTrue(nn.out_queue.empty())
        self.assertEqual(str(nn2.oan_id), "00000000-0000-babe-0000-000000000000")
        self.assertEqual(host, "remotehost")
        self.assertEqual(port, 1338)
        self.assertEqual(blocked, True)
        self.assertEqual(state, OANNetworkNodeState.DISCONNECTED)
        self.assertTrue(nn2.is_disconnected())
        self.assertFalse(nn2.has_heartbeat_state(OANHeartbeat.OFFLINE))

    def test_network_node_queue(self):
        class TestMessage(object):
            value = None

        nn = OANNetworkNode.create(
            UUID("00000000-0000-dead-0000-000000000000"),
            "localhost", 1337, False
        )
        self.assertTrue(nn.out_queue.empty())

        message = TestMessage()
        message.value = "test"
        nn.send(message)

        pop_message = nn.out_queue.get()
        self.assertTrue(isinstance(pop_message, TestMessage))
        self.assertEqual(pop_message.value, message.value)



    def test_network_node_message_statistic(self):
        nn = OANNetworkNode.create(
            UUID("00000000-0000-dead-0000-000000000000"),
            "localhost", 1337, False
        )

        (sent_time, out_time, out_count,
            in_time, in_count) = nn.get_message_statistic("command")

        self.assertTrue(sent_time is None)
        self.assertTrue(out_time is None)
        self.assertEqual(out_count, 0)
        self.assertTrue(in_time is None)
        self.assertEqual(in_count, 0)

        nn.add_message_statistic("command", sent_time = True)

        (sent_time, out_time, out_count,
            in_time, in_count) = nn.get_message_statistic("command")

        self.assertTrue(sent_time is not None)
        self.assertTrue(out_time is None)
        self.assertEqual(out_count, 0)
        self.assertTrue(in_time is None)
        self.assertEqual(in_count, 0)

        nn.add_message_statistic("command", out_time = True)

        (sent_time, out_time, out_count,
            in_time, in_count) = nn.get_message_statistic("command")

        self.assertTrue(sent_time is not None)
        self.assertTrue(out_time is not None)
        self.assertEqual(out_count, 1)
        self.assertTrue(in_time is None)
        self.assertEqual(in_count, 0)

        nn.add_message_statistic("command", in_time = True)

        (sent_time, out_time, out_count,
            in_time, in_count) = nn.get_message_statistic("command")

        self.assertTrue(sent_time is not None)
        self.assertTrue(out_time is not None)
        self.assertEqual(out_count, 1)
        self.assertTrue(in_time is not None)
        self.assertEqual(in_count, 1)













