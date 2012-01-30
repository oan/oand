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

from oan.network.network_node import OANNetworkNode

class TestOANNetworkNode(OANTestCase):
    def test_network_node(self):
        nn = OANNetworkNode("oan_id")

        self.assertEqual(nn.oan_id, "oan_id")
        self.assertEqual(nn.host, None)
        self.assertEqual(nn.port, None)
        self.assertEqual(nn.blocked, None)
        self.assertTrue(nn.is_disconnected())
        self.assertTrue(nn.heartbeat.is_offline())

    def test_network_node_create(self):
        nn = OANNetworkNode.create(
            "oan_id",
            "localhost",
            "1337",
            False
        )
        self.assertEqual(nn.oan_id, "oan_id")
        self.assertEqual(nn.host, "localhost")
        self.assertEqual(nn.port, "1337")
        self.assertEqual(nn.blocked, False)
        self.assertTrue(nn.is_disconnected())
        self.assertTrue(nn.heartbeat.is_offline())
        print nn


"""
    def validate_network_node(self, nn):
        self.assertEqual(nn.oan_id, "oan_id")
        self.assertEqual(nn.oan_id, "oan_id")
        self.assertEqual(nn.name, "name")
        self.assertEqual(nn.domain_name, "domain_name")
        self.assertEqual(nn.port, "port")
        self.assertEqual(nn.heartbeat.value, "2006-06-06T06:06:06Z")

        self.assertEqual(nn.connection_url, "domain_name:port")
        self.assertTrue(nn.is_valid())
"""

"""
    def test_get_dict(self):
        nn = OANNetworkNode("oan_id", "name", "domain_name", "port")

        param = {}
        param['oan_id'] = "oan_id"
        param['name'] = "name"
        param['domain_name'] = "domain_name"
        param['port'] = "port"
        param['last_heartbeat'] = "2006-06-06T06:06:06Z"

        self.assertEqual(nn.get_dict(), param)

    def test_create_from_dict(self):
        param = {}
        param['oan_id'] = "oan_id"
        param['name'] = "name"
        param['domain_name'] = "domain_name"
        param['port'] = "port"
        param['last_heartbeat'] = "2006-06-06T06:06:06Z"

        nn = OANNetworkNode.create_from_dict(param)
        self.validate_network_node(nn)
"""

