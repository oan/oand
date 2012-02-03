#!/usr/bin/env python
'''
Test cases for oan.data_manager.py

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from test.test_case import OANTestCase

from oan.data_manager import OANDataManager

class TestOanManager(OANTestCase):
    dm = None

    def setUp(self):
        # Clear all data in the database the first time the unit test is
        # executed. Create a new instance for each unit test function, to
        # reload data from database.
        if (self.dm == None):
            self.dm = OANDataManager("unittest-data.dat")
            self.dm.truncate()
        else:
            self.dm = OANDataManager("unittest-data.dat")

    def test_oan(self):
        self.assertFalse(self.dm.exist("/movies/alien.avi"))
        self.assertRaises(Exception, self.dm.get, "/movies/alien.avi")

        self.assertEqual(self.dm.set("/movies/alien.avi", "Value"), None)
        self.assertEqual(self.dm.get("/movies/alien.avi"), "Value")
        self.assertTrue(self.dm.exist("/movies/alien.avi"))

        self.assertEqual(self.dm.delete("/movies/alien.avi"), None)
        self.assertFalse(self.dm.exist("/movies/alien.avi"))
        self.assertRaises(Exception, self.dm.get, "/movies/alien.avi")

    def test_oan_list(self):
        # Prepare db
        self.assertEqual(self.dm.set("/movies/alien.avi", "Value"), None)
        self.assertEqual(self.dm.set("/movies/aliens.avi", "Value"), None)
        self.assertEqual(self.dm.set("/movies/Terminator-2.avi", "Value"), None)

        # Test if all files are listed.
        movies_list = []
        movies_list.append("alien.avi")
        movies_list.append("aliens.avi")
        movies_list.append("Terminator-2.avi")

        self.assertEqual(self.dm.list("/movies/"), movies_list)
