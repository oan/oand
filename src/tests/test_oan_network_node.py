#!/usr/bin/env python
'''
Test cases for oand.

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import unittest

#from networknode import NetworkNode

#class TestNetworkNode(unittest.TestCase):
#    _network_node = None

#    def setUp(self):
#        self._network_node = NetworkNode('leet-server', 'leetsrv.com', '1337')

#    def test_defaults(self):
#        self.assertEqual(self._network_node.get_last_heartbeat(), "2006-06-06 06:06:06")

#    def test_touch_last_heartbeat(self):
#        self._network_node.touch_last_heartbeat()
#        self.assertEqual(self._network_node.is_heartbeat_expired(), False)
#        self.assertEqual(self._network_node.is_node_inactive(), False)

#    def test_is_heartbeat_expired(self):
#        self._network_node.set_last_heartbeat("2011-01-01 01:01:01")
#        self.assertEqual(self._network_node.is_heartbeat_expired(), True)
#        self.assertEqual(self._network_node.is_node_inactive(), True)

#    def test_get_last_heartbeat(self):
#        heartbeat = "2011-01-01 01:01:01"
#        self._network_node.set_last_heartbeat(heartbeat)
#        self.assertEqual(self._network_node.get_last_heartbeat(), heartbeat)

#    def test_is_valid(self):
#        self.assertEqual(self._network_node.is_valid(), True)

if __name__ == '__main__':
    unittest.main()