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

#from oan_unittest import OANUnitTest
#from oand import OAND
#from networknode import CircularNetworkNode
#from config import Config

#class TestOand(OANUnitTest):
#    def test_start_sol_server(self):
#        self._sol_server = OAND.create_localnetwork_circular_node(
#            Config('sol-server', "localhost", "4000"))

#        self.assertEqual(self._sol_server.get_network_node().get_dbg_nodes(),
#                         "None - sol-server - None")

#        self._mapa_book = OAND.create_localnetwork_circular_node(
#            Config('mapa-book', "localhost", "4001",
#                   'sol-server', "localhost", "4000"))

#        self.assertEqual(self._sol_server.get_network_node().get_dbg_nodes(),
#                         "mapa-book - sol-server - mapa-book")

#        self._asp_server = OAND.create_localnetwork_circular_node(
#            Config('asp-server', "localhost", "4002",
#                   'sol-server', "localhost", "4000"))

#        self.assertEqual(self._sol_server.get_network_node().get_dbg_nodes(),
#                         "asp-server - sol-server - mapa-book")

#        self._dali_book = OAND.create_localnetwork_circular_node(
#            Config('dali-book', "localhost", "4003",
#                  'asp-server',"localhost", "4002"))

#        # Test state after all server has started.
#        self.assertEqual(self._sol_server.get_network_node().get_dbg_nodes(),
#                         "asp-server - sol-server - mapa-book")
#        self.assertEqual(self._mapa_book.get_network_node().get_dbg_nodes(),
#                         "sol-server - mapa-book - dali-book")
#        self.assertEqual(self._dali_book.get_network_node().get_dbg_nodes(),
#                         "mapa-book - dali-book - asp-server")
#        self.assertEqual(self._asp_server.get_network_node().get_dbg_nodes(),
#                         "dali-book - asp-server - sol-server")

if __name__ == '__main__':
    unittest.main()
