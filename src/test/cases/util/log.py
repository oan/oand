#!/usr/bin/env python
'''
Test cases for util.log

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from test.test_case import OANTestCase

from oan.util import log

class TestLogging(OANTestCase):

    def test__get_numeric_log_level(self):
        self.assertEqual(log._get_numeric_log_level(100), 100)
        self.assertEqual(log._get_numeric_log_level("100"), 100)

        self.assertEqual(log._get_numeric_log_level("NONE"), 100)
        self.assertEqual(log._get_numeric_log_level("DEBUG"), 10)
        self.assertEqual(log._get_numeric_log_level("INFO"), 20)
        self.assertEqual(log._get_numeric_log_level("WARNING"), 30)
        self.assertEqual(log._get_numeric_log_level("ERROR"), 40)
        self.assertEqual(log._get_numeric_log_level("CRITICAL"), 50)

        self.assertEqual(log._get_numeric_log_level("Not existing"), 100)
