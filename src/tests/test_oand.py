#!/usr/bin/env python
'''
Test cases for oand.

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We own it all"
__version__ = "0.1"
__status__ = "Test"

import unittest
from test import test_support

from oand import Config

class TestConfig(unittest.TestCase):
  serverName = "this-is-a-server-name"
  
  def setUp(self):
    self.config = Config(self.serverName)

  def test_getServerName(self):
    self.assertEqual(self.config.getServerName(), self.serverName)

if __name__ == '__main__':
  unittest.main()