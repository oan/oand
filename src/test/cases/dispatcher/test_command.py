#!/usr/bin/env python
"""
Test cases for oan.dispatcher.command.

"""

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import mock

from test.test_case import OANTestCase
from oan import manager
from oan.manager import node_manager
from oan.config import OANConfig
from oan.node_manager.node_manager import OANNodeManager
from oan.dispatcher.dispatcher import OANDispatcher

class TestOANCommand(OANTestCase):

    mock_database = None

    def setUp(self):
        mock_shutdown = mock.Mock()
        mock_shutdown.shutdown.return_value = True

        self.mock_database = mock.MagicMock()
        self.mock_database.shutdown.return_value = True

        config = OANConfig(
            "00000000-0000-dead-0000-000000000000",
            "TestDispatcherCommands",
            "localhost",
            str(9000)
        )

        manager.setup(
            mock_shutdown,
            self.mock_database,
            OANDispatcher(),
            mock_shutdown,
            mock_shutdown,
            OANNodeManager(config)
        )

        node_manager().load()

    def tearDown(self):
        manager.shutdown()
