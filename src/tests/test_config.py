#!/usr/bin/env python
'''
Test cases for oand.

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import unittest
from config import Config

class TestConfig(unittest.TestCase):
    _config = None
    _server_name = "this-is-a-server-name"
    _server_domain_name = "www.cybercow.se"
    _server_port = "4000"
    _bff_name = "LeetServer"
    _bff_domain_name = "node1.cybecow.se"
    _bff_port = "1337"

    def setUp(self):
        # pylint: disable-msg=C0103
        self._config = Config(
          self._server_name,
          self._server_domain_name,
          self._server_port,
          self._bff_name,
          self._bff_domain_name,
          self._bff_port
        )

    def test_get_server_name(self):
        self.assertEqual(self._config.get_server_name(), self._server_name)

    def test_get_server_domain_name(self):
        self.assertEqual(self._config.get_server_domain_name(),
                         self._server_domain_name)

    def test_get_server_port(self):
        self.assertEqual(self._config.get_server_port(), self._server_port)

    def test_get_bff_name(self):
        self.assertEqual(self._config.get_bff_name(), self._bff_name)

    def test_get_bff_domain_name(self):
        self.assertEqual(self._config.get_bff_domain_name(),
                         self._bff_domain_name)

    def test_get_bff_port(self):
        self.assertEqual(self._config.get_bff_port(), self._bff_port)

class TestConfigLoadFromFile(TestConfig):
    def setUp(self):
        # pylint: disable-msg=C0103
        self._config = Config.from_filename("./tests/oand.cfg")

    def test_file_not_exist(self):
        self.assertRaises(IOError,
                          Config.from_filename, ("file-not-exist.cfg"))

if __name__ == '__main__':
    unittest.main()