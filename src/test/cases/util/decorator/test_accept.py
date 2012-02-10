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

from oan.util.decorator.accept import IGNORE, accepts, returns


class TestType:
    def __str__(self):
        return "my test type"

@accepts(int)
@returns(int)
def func_int(int_var):
    return int_var

@accepts(int, tuple, float, str, list, dict, TestType)
@returns(str)
def func_full(a, b, c, d, e, f, g):
    return "%s,%s,%s,%s,%s,%s,%s" % (a, b, c, d, e, f, g)


@accepts(str, str, str)
@returns(str)
def func_named(arg1 = None, arg2 = None, arg3 = None):
    return "%s,%s,%s" % (arg1, arg2, arg3)

class TestLogging(OANTestCase):

    @accepts(IGNORE, int)
    @returns(int)
    def member_int(self, int_var):
        return int_var

    def atest_func(self):
        self.assertEqual(func_int(10), 10)

        with self.assertRaises(TypeError):
            func_int(10.0)

        with self.assertRaises(TypeError):
            func_int("10")

    def atest_member(self):
        self.assertEqual(self.member_int(10), 10)

        with self.assertRaises(TypeError):
            self.member_int(10.0)

        with self.assertRaises(TypeError):
            self.member_int("10")

    def atest_func_full(self):
        self.assertEqual(
            func_full(55, (22,"22"), 10.0, "str", [1,2,"3"], {"dict": 1}, TestType()),
            "55,(22, '22'),10.0,str,[1, 2, '3'],{'dict': 1},my test type"
        )

    def test_func_named(self):
        with self.assertRaises(AssertionError):
            self.assertEqual(
                func_named(arg1="bli", arg2 = 'b value', arg3="kalle"),
                ""
            )


