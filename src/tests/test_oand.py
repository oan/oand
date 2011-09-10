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
from oand import OAND, CircularNetworkNode
from config import Config

class TestOand(unittest.TestCase):
    _network_node_class = CircularNetworkNode

    def test_start_sol_server(self):
        self._sol_server = OAND()
        self._sol_server.start_deamon(self._network_node_class, Config(
            'sol-server', "localhost", "4000"))

        self.assertEqual(self._sol_server.get_network_node().get_dbg_nodes(),
                         "None - sol-server - None")

        self._mapa_book = OAND()
        self._mapa_book.start_deamon(self._network_node_class, Config(
            'mapa-book', "localhost", "4001",
            'sol-server', "localhost", "4000"))

        self.assertEqual(self._sol_server.get_network_node().get_dbg_nodes(),
                         "mapa-book - sol-server - mapa-book")

        self._asp_server = OAND()
        self._asp_server.start_deamon(self._network_node_class, Config(
            'asp-server', "localhost", "4002",
            'sol-server', "localhost", "4000"))

        self.assertEqual(self._sol_server.get_network_node().get_dbg_nodes(),
                         "asp-server - sol-server - mapa-book")

        self._dali_book = OAND()
        self._dali_book.start_deamon(self._network_node_class,Config(
            'dali-book', "localhost", "4003",
            'asp-server',"localhost", "4002"))

        # Test state after all server has started.
        self.assertEqual(self._sol_server.get_network_node().get_dbg_nodes(),
                         "asp-server - sol-server - mapa-book")
        self.assertEqual(self._sol_server.get_network_node().get_dbg_nodes(),
                         "asp-server - sol-server - mapa-book")
        self.assertEqual(self._sol_server.get_network_node().get_dbg_nodes(),
                         "asp-server - sol-server - mapa-book")
        self.assertEqual(self._sol_server.get_network_node().get_dbg_nodes(),
                         "asp-server - sol-server - mapa-book")



if __name__ == '__main__':
    unittest.main()