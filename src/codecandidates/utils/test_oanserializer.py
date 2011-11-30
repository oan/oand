#!/usr/bin/env python
'''
Test OANSerializer.

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import unittest
import OANSerializer

class Test(object):
    def __init__(self, name= None, content = None):
        self.name = name
        self.content = content

    def get_name(self):
        return self.name

OANSerializer.add("Test", Test)

class TestOANSerializer(unittest.TestCase):

    def test_exist(self):
        c1 = Test("c1", "file 1")

        txt = OANSerializer.encode(c1)
        obj = OANSerializer.decode(txt)

        self.assertEqual(obj.get_name(), "c1")
        self.assertEqual(obj.content, "file 1")

if __name__ == '__main__':
    unittest.main()
