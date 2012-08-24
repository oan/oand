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
def key_argument(arg1 = None, arg2 = None, arg3 = None):
    return "%s,%s,%s" % (arg1, arg2, arg3)

class TestLogging(OANTestCase):

    @accepts(IGNORE, int)
    @returns(int)
    def member_int(self, int_var):
        return int_var

    @accepts(IGNORE, int, int)
    @returns(int)
    def member_two_arg(self, var1, var2):
        return var1 + var2

    @accepts(IGNORE, int, IGNORE)
    @returns(int)
    def member_default_value(self, int_var, def_var = 0):
        return int_var + def_var

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

    def test_default_value(self):
        self.assertEqual(self.member_default_value(10), 10)
        self.assertEqual(self.member_default_value(10, 10), 20)

        with self.assertRaises(TypeError):
            self.member_default_value(10.0)

        with self.assertRaises(TypeError):
            self.member_default_value("10")

        with self.assertRaises(TypeError):
            self.member_default_value(10,20,30,40)

    def test_invalid_number_of_args(self):
        self.assertEqual(self.member_int(10), 10)
        with self.assertRaises(TypeError):
            self.member_int(1,2)

        self.assertEqual(self.member_two_arg(1,2), 3)
        with self.assertRaises(TypeError):
            self.member_two_arg(1)

    def test_func_full(self):
        self.assertEqual(
            func_full(55, (22,"22"), 10.0, "str", [1,2,"3"], {"dict": 1}, TestType()),
            "55,(22, '22'),10.0,str,[1, 2, '3'],{'dict': 1},my test type"
        )

    def test_key_argument(self):
        with self.assertRaises(AssertionError):
            self.assertEqual(
                key_argument(arg1="bli", arg2 = 'b value', arg3="kalle"),
                ""
            )


