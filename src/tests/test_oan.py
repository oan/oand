#!/usr/bin/env python
'''
Test cases for oan.py

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from oan_unittest import OANTestCase

import oan
from oan import loop, database, dispatcher, node_manager

from oan_node_manager import OANNodeManager
from oan_meta_manager import OANMetaManager
from oan_data_manager import OANDataManager
from oan_loop import OANLoop
from oan_database import OANDatabase
from oan_config import OANConfig
from oan_message import OANMessageDispatcher

class TestOan(OANTestCase):
    def setUp(self):
        pass

    def test_oan(self):
        self.assertRaises(Exception, oan.validate)

        config = OANConfig(
                '00000000-0000-aaaa-0000-000000000000',
                "TestOANDatabase",
                "localhost",
                str(9000))

        oan.set_managers(
            OANLoop(),
            OANDatabase(config),
            OANMessageDispatcher(config),
            OANDataManager("unittest-data.dat"),
            OANMetaManager(),
            OANNodeManager(config)
        )

        oan.validate()

