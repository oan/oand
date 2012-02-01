#!/usr/bin/env python
'''
Test cases for util.decorator

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from test.test_case import OANTestCase

from oan.util.decorator.const import const

class Constants(object):
    @const
    VAR=12

    @constant
    def FOO():
        return 0xBAADFACE

# class TestLogging(OANTestCase):

#     def test_sync(self):
#         pass

#     @accepts(int)
#     def moo(self, moo):
#         print moo
