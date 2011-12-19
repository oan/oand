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

from oan_unittest import OANUnitTest

import oan
from oan_node_manager import OANNodeManager
from oan_meta_manager import OANMetaManager
from oan_data_manager import OANDataManager

class TestOan(OANUnitTest):
    def setUp(self):
        pass

    def test_oan(self):
        self.assertRaises(Exception, oan.validate)

        oan.set_managers(
            OANDataManager("unittest-data.dat"),
            OANMetaManager(),
            OANNodeManager()
        )
        oan.validate()
