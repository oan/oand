#!/usr/bin/env python
'''
Test oan_event

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from oan_unittest import OANTestCase
from oan_event import *

class TestOANEvent(OANTestCase):

    def f(self, x, args):
        args.append('f(%s)' % x)

    def g(self, x, args):
        args.append('g(%s)' % x)

    def test_event1(self):
        e = OANEvent()
        e.append(self.f)

        args = []
        e(123, args)

        self.assertEqual(args, ['f(123)'])

    def test_event2(self):
        e = OANEvent()
        e += (self.f, self.g)

        args = []
        e(124, args)
        self.assertEqual(args, ['f(124)', 'g(124)'] )

        args = []
        e(125, args)
        self.assertEqual(args, ['f(125)', 'g(125)'] )

        del e[0]
        args = []
        e(126, args)
        self.assertEqual(args, ['g(126)'])
