#!/usr/bin/env python
"""
Test cases for oan.network.network_node.py

"""

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from test.test_case import OANTestCase

from oan.network.network_node import OANNetworkNode, OANNetworkNodeState

class TestOANNetworkNode(OANTestCase):
    def test_network_node_empty(self):
        nn = OANNetworkNode("oan_id")

        (name, host, port, blocked, state, heartbeat) = nn.get()

        self.assertTrue(nn.out_queue.empty())
        self.assertEqual(nn.oan_id, "oan_id")
        self.assertEqual(host, None)
        self.assertEqual(port, None)
        self.assertEqual(blocked, None)
        self.assertEqual(state, OANNetworkNodeState.DISCONNECTED)
        self.assertTrue(nn.is_disconnected())
        self.assertTrue(nn.is_offline())

    def test_network_node_create(self):
        nn = OANNetworkNode.create("oan_id", "localhost", "1337", False)

        (name, host, port, blocked, state, heartbeat) = nn.get()

        self.assertTrue(nn.out_queue.empty())
        self.assertEqual(nn.oan_id, "oan_id")
        self.assertEqual(host, "localhost")
        self.assertEqual(port, 1337)
        self.assertEqual(blocked, False)
        self.assertEqual(state, OANNetworkNodeState.DISCONNECTED)
        self.assertTrue(nn.is_disconnected())
        self.assertTrue(nn.is_offline())

    def test_network_node_update(self):
        nn = OANNetworkNode.create("oan_id", "localhost", "1337", False)
        nn.update(
            "your-node", "remotehost", "1338",
            True, OANNetworkNodeState.CONNECTING,
            "2107-07-07T07:07:07Z"
        )

        (name, host, port, blocked, state, heartbeat) = nn.get()

        self.assertTrue(nn.out_queue.empty())
        self.assertEqual(nn.oan_id, "oan_id")
        self.assertEqual(host, "remotehost")
        self.assertEqual(port, 1338)
        self.assertEqual(blocked, True)
        self.assertEqual(state, OANNetworkNodeState.CONNECTING)
        self.assertFalse(nn.is_disconnected())
        self.assertFalse(nn.is_offline())

    def test_network_node_serialize(self):
        nn = OANNetworkNode.create("oan_id", "localhost", "1337", False)
        nn.update(
            "your-node", "remotehost", "1338",
            True, OANNetworkNodeState.CONNECTING,
            "2107-07-07T07:07:07Z"
        )
        data = nn.serialize()

        nn2 = OANNetworkNode("new_id")
        nn2.unserialize(data)

        (name, host, port, blocked, state, heartbeat) = nn2.get()

        self.assertTrue(nn.out_queue.empty())
        self.assertEqual(nn2.oan_id, "new_id")
        self.assertEqual(host, "remotehost")
        self.assertEqual(port, 1338)
        self.assertEqual(blocked, True)
        self.assertEqual(state, OANNetworkNodeState.DISCONNECTED)
        self.assertTrue(nn2.is_disconnected())
        self.assertFalse(nn2.is_offline())

    def test_network_node_queue(self):
        class TestMessage(object):
            value = None

        nn = OANNetworkNode("oan_id")
        self.assertTrue(nn.out_queue.empty())

        message = TestMessage()
        message.value = "test"
        nn.send(message)

        pop_message = nn.out_queue.get()
        self.assertTrue(isinstance(pop_message, TestMessage))
        self.assertEqual(pop_message.value, message.value)
