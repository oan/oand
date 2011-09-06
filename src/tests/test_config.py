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

from config import Config

class TestConfig(unittest.TestCase):
  serverName = "this-is-a-server-name"
  serverDomainName = "www.cybercow.se"
  serverPort = "4000"
  bffNode = "node1.cybecow.se"

  def setUp(self):
    self.config = Config(self.serverName,
      self.serverDomainName,
      self.serverPort,
      self.bffNode
    )

  def test_getServerName(self):
    self.assertEqual(self.config.getServerName(), self.serverName)

  def test_getServerDomainName(self):
    self.assertEqual(self.config.getServerDomainName(), self.serverDomainName)

  def test_getServerPort(self):
    self.assertEqual(self.config.getServerPort(), self.serverPort)

  def test_getBffNode(self):
    self.assertEqual(self.config.getBffNode(), self.bffNode)

class TestConfigLoadFromFile(TestConfig):
  def setUp(self):
    self.config = Config.fromFilename("./tests/oand.cfg")

  def test_fileNotExist(self):
    self.assertRaises(IOError, Config.fromFilename, ("file-not-exist.cfg"))

if __name__ == '__main__':
  unittest.main()