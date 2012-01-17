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

from test.test_case import OANTestCase
from oan.heartbeat import *

class TestOANHeartbeat(OANTestCase):

    def test_heartbeat(self):
        '''
        Also called from test_resources

        '''
        hb = OANHeartbeat()

        self.assertEqual(hb.is_idle(), True)
        self.assertEqual(hb.is_expired(), True)
        self.assertEqual(hb.is_offline(), True)
        self.assertEqual(hb.is_dead(), False)

        hb.value = "2106-06-06T06:06:06Z"
        self.assertEqual(hb.is_idle(), False)
        self.assertEqual(hb.is_expired(), False)
        self.assertEqual(hb.is_offline(), False)
        self.assertEqual(hb.is_dead(), False)
        self.assertEqual(hb.value, "2106-06-06T06:06:06Z")
        self.assertEqual(hb.time, "06:06:06")

        hb.touch()
        self.assertEqual(hb.is_idle(), False)
        self.assertEqual(hb.is_expired(), False)
        self.assertEqual(hb.is_offline(), False)
        self.assertEqual(hb.is_dead(), False)

        hb.set_idle()
        self.assertEqual(hb.is_idle(), True)
        self.assertEqual(hb.is_expired(), False)
        self.assertEqual(hb.is_offline(), False)
        self.assertEqual(hb.is_dead(), False)

        hb.set_expired()
        self.assertEqual(hb.is_idle(), True)
        self.assertEqual(hb.is_expired(), True)
        self.assertEqual(hb.is_offline(), False)
        self.assertEqual(hb.is_dead(), False)

        hb.set_offline()
        self.assertEqual(hb.is_idle(), True)
        self.assertEqual(hb.is_expired(), True)
        self.assertEqual(hb.is_offline(), True)
        self.assertEqual(hb.is_dead(), False)

        hb.set_dead()
        self.assertEqual(hb.is_idle(), True)
        self.assertEqual(hb.is_expired(), True)
        self.assertEqual(hb.is_offline(), True)
        self.assertEqual(hb.is_dead(), True)

        self.assertRaises(ValueError, hb.set_value, "NOT-A-VALID-DATE")
        self.assertRaises(ValueError, hb.set_value, "")

    def test_heartbeat_operators(self):
        low = OANHeartbeat()
        low.value = "2006-06-06T06:06:06Z"

        high = OANHeartbeat()
        same = OANHeartbeat()
        high.value = same.value = "2106-06-06T06:06:06Z"

        self.assertTrue(low < high)
        self.assertTrue(high > low)
        self.assertTrue(high == same)
        self.assertTrue(high != low)

        self.assertFalse(low > high)
        self.assertFalse(high < low)
        self.assertFalse(high == low)

if __name__ == '__main__':
    unittest.main()
