#!/usr/bin/env python
"""
Test oan.async.serializer.

"""

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from test.test_case import OANTestCase

from oan.network import serializer

class Test(object):
    def __init__(self, name= None, content = None):
        self.name = name
        self.content = content

    def get_name(self):
        return self.name

serializer.add(Test)

class TestOANSerializer(OANTestCase):

    def test_exist(self):
        c1 = Test("c1", "file 1")

        txt = serializer.encode(c1)
        obj = serializer.decode(txt)

        self.assertEqual(obj.get_name(), "c1")
        self.assertEqual(obj.content, "file 1")
