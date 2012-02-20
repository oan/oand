#!/usr/bin/env python
"""
Test cases for oan.manager

"""

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import mock

from test.test_case import OANTestCase

from oan.manager import (
    network, dispatcher, database, data_manager, meta_manager, node_manager,
    OANNetworkManagerError
)
from oan import manager

class TestManager(OANTestCase):
    def test_managers(self):
        with self.assertRaises(OANNetworkManagerError):
            manager.validate()

        manager.setup(
            "data_manager",
            "meta_manager",
            "node_manager",
            "database",
            "dispatcher",
            "network"
        )
        self.assertTrue(manager.validate())

        self.assertEqual(data_manager(), "data_manager")
        self.assertEqual(meta_manager(), "meta_manager")
        self.assertEqual(node_manager(), "node_manager")
        self.assertEqual(dispatcher(), "dispatcher")
        self.assertEqual(database(), "database")
        self.assertEqual(network(), "network")

    def test_shutdown(self):
        mock_shutdown = mock.Mock()
        mock_shutdown.shutdown.return_value = True

        manager.setup(
            mock_shutdown,
            mock_shutdown,
            mock_shutdown,
            mock_shutdown,
            mock_shutdown,
            mock_shutdown
        )
        self.assertTrue(manager.shutdown())

        mock_shutdown.shutdown.return_value = False
        with self.assertRaises(OANNetworkManagerError):
            manager.shutdown()
