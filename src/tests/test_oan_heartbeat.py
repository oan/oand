#!/usr/bin/env python
'''
Test heartbeat

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import unittest
from oan_heartbeat import *

class TestOANHeartBeat(unittest.TestCase):

    def test_heartbeat(self):
        '''
        Also called from test_resources

        '''
        hb = OANHeartBeat()

        self.assertEqual(hb.is_expired(), True)
        self.assertEqual(hb.is_inactive(), True)
        self.assertEqual(hb.is_dead(), True)

        hb.value = "2106-06-06T06:06:06Z"
        self.assertEqual(hb.is_expired(), False)
        self.assertEqual(hb.is_inactive(), False)
        self.assertEqual(hb.is_dead(), False)
        self.assertEqual(hb.value, "2106-06-06T06:06:06Z")

        hb.touch()
        self.assertEqual(hb.is_expired(), False)
        self.assertEqual(hb.is_inactive(), False)
        self.assertEqual(hb.is_dead(), False)

        hb.set_expired()
        self.assertEqual(hb.is_expired(), True)
        self.assertEqual(hb.is_inactive(), False)
        self.assertEqual(hb.is_dead(), False)

        hb.set_inactive()
        self.assertEqual(hb.is_expired(), True)
        self.assertEqual(hb.is_inactive(), True)
        self.assertEqual(hb.is_dead(), False)

        hb.set_dead()
        self.assertEqual(hb.is_expired(), True)
        self.assertEqual(hb.is_inactive(), True)
        self.assertEqual(hb.is_dead(), True)

        self.assertRaises(ValueError, hb.set_value, "NOT-A-VALID-DATE")
        self.assertRaises(ValueError, hb.set_value, "")

if __name__ == '__main__':
    unittest.main()
