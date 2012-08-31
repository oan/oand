#!/usr/bin/env python
"""
Cube node representation.

"""

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from uuid import UUID

from oan.util import log
from oan.util.decorator.accept import IGNORE, accepts, returns
from oan.heartbeat import OANHeartbeat


class OANCubeNodeState(object):
    """States a cube node connection can be in."""
    DISCONNECTED, CONNECTING, CONNECTED = range(1, 4)


class OANCubeNode:
    # A unique UUID representing this node.
    oan_id = None

    # A non unique name which the node is known as.
    name = None

    # A tuple with the external ip-number or domain for node and port on which
    # the node listening for oan connections.
    url = None

    # The current connection state of bridge connection between
    # local node and this remote node.
    state = None

    # Keep online state for this node.
    heartbeat = None

    @accepts(IGNORE, UUID, IGNORE)
    def __init__(self, oan_id, url = (None, None)):
        self.oan_id = oan_id
        self.state = OANCubeNodeState.DISCONNECTED
        self.url = url
        self.heartbeat = OANHeartbeat()

    @accepts(IGNORE, dict)
    def unserialize(self, data):
        """Recreate node from dict produced by serialize."""
        self.name = data["name"]
        self.url = data["url"]
        self.heartbeat.set_value(data["heartbeat"])
        self.state = OANCubeNodeState.DISCONNECTED

    @returns(dict)
    def serialize(self):
        """
        Return a dict that can be used to recreate this node with serialize.

        """
        return {
            "name": self.name,
            "url": self.url,
            "heartbeat": self.heartbeat.value,
        }

    @returns(bool)
    def is_disconnected(self):
        """The network connection to this node is not active."""
        return self.state == OANCubeNodeState.DISCONNECTED

    def __str__(self):
        return 'OANCubeNode(%s, %s) S(%s) hb(%s)' % (
            self.oan_id, self.url,
            self.state,
            self.heartbeat.time
        )

    def __repr__(self):
        return "CubeNode: %s" % str(self.url)


from test.test_case import OANTestCase

class TestOANCubeNode(OANTestCase):
    def test_network_node_invalid_uuid(self):
        with self.assertRaises(TypeError):
            OANCubeNode("invalid-id")

    def test_network_node_empty(self):
        nn = OANCubeNode(UUID("00000000-0000-dead-0000-000000000000"))

        self.assertEqual(str(nn.oan_id), "00000000-0000-dead-0000-000000000000")
        self.assertEqual(nn.url, (None, None))
        self.assertEqual(nn.state, OANCubeNodeState.DISCONNECTED)
        self.assertTrue(nn.is_disconnected())
        self.assertTrue(nn.heartbeat.has_state(OANHeartbeat.OFFLINE))

    def test_network_node_create(self):
        nn = OANCubeNode(
            UUID("00000000-0000-dead-0000-000000000000"),
            ("localhost", 1337)
        )

        self.assertEqual(str(nn.oan_id), "00000000-0000-dead-0000-000000000000")
        self.assertEqual(nn.url, ('localhost', 1337))
        self.assertEqual(nn.state, OANCubeNodeState.DISCONNECTED)
        self.assertTrue(nn.is_disconnected())
        self.assertTrue(nn.heartbeat.has_state(OANHeartbeat.OFFLINE))


    def test_network_node_update(self):
        nn = OANCubeNode(
            UUID("00000000-0000-dead-0000-000000000000"),
            ("localhost", 1337)
        )

        nn.name = "your-node",
        nn.url = ("remotehost", 1338)
        nn.state = OANCubeNodeState.CONNECTING
        nn.heartbeat.set_value("2107-07-07T07:07:07Z")

        self.assertEqual(str(nn.oan_id), "00000000-0000-dead-0000-000000000000")
        self.assertEqual(nn.url, ('remotehost', 1338))
        self.assertEqual(nn.state, OANCubeNodeState.CONNECTING)
        self.assertFalse(nn.is_disconnected())
        self.assertFalse(nn.heartbeat.has_state(OANHeartbeat.OFFLINE))

    def test_network_node_serialize(self):
        nn = OANCubeNode(
            UUID("00000000-0000-dead-0000-000000000000"),
            ("localhost", 1337)
        )

        nn.name = "your-node",
        nn.url = ("remotehost", 1338)
        nn.state = OANCubeNodeState.CONNECTING
        nn.heartbeat.set_value("2107-07-07T07:07:07Z")

        data = nn.serialize()
        nn2 = OANCubeNode(UUID("00000000-0000-dead-0000-000000000000"))
        nn2.unserialize(data)

        self.assertEqual(str(nn.oan_id), "00000000-0000-dead-0000-000000000000")
        self.assertEqual(nn.url, ('remotehost', 1338))
        self.assertEqual(nn.state, OANCubeNodeState.CONNECTING)
        self.assertFalse(nn.is_disconnected())
        self.assertFalse(nn.heartbeat.has_state(OANHeartbeat.OFFLINE))

