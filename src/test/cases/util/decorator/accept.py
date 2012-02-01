#!/usr/bin/env python
"""
Test cases for synchronized decorator in oan.util.decorator.accept

"""

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from test.test_case import OANTestCase

from oan.util.decorator.accept import accepts, returns

@accepts(int)
@returns(int)
def func_int(int_var):
    return int_var

@accepts(int, tuple, float, str, list, dict)
@returns(str)
def func_full(a, b, c, d, e, f):
    return "%s,%s,%s,%s,%s,%s" % (a, b, c, d, e, f)


class TestLogging(OANTestCase):

    @accepts(object, int)
    @returns(int)
    def member_int(self, int_var):
        return int_var

    def test_func(self):
        self.assertEqual(func_int(10), 10)

        with self.assertRaises(TypeError):
            func_int(10.0)

        with self.assertRaises(TypeError):
            func_int("10")

    def test_member(self):
        self.assertEqual(self.member_int(10), 10)

        with self.assertRaises(TypeError):
            self.member_int(10.0)

        with self.assertRaises(TypeError):
            self.member_int("10")

    def test_func_full(self):
        self.assertEqual(
            func_full(55, (22,"22"), 10.0, "str", [1,2,"3"], {"dict": 1}),
            "55,(22, '22'),10.0,str,[1, 2, '3'],{'dict': 1}"
        )
