#!/usr/bin/env python
'''
Test cases for Config.

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

    # Options
    opts = {}
    opts["verbose"] = 5
    opts["config"] = "/tmp/oand.cfg"
    opts["pid_file"] = "/tmp/oand.pid"
    opts["log_file"] = "/log/oand.log"

    opts["server_name"] = "this-is-a-server-name"
    opts["server_domain_name"] = "www.cybercow.se"
    opts["server_port"] = "4000"
    opts["bff_name"] = "LeetServer"
    opts["bff_domain_name"] = "node1.cybecow.se"
    opts["bff_port"] = "1337"

    def setUp(self):
        self._config = Config(
          self.opts["server_name"],
          self.opts["server_domain_name"],
          self.opts["server_port"],
          self.opts["bff_name"],
          self.opts["bff_domain_name"],
          self.opts["bff_port"]
        )

    def test_config(self):
        cnf = self._config
        self.assertEqual(cnf.server_name, self.opts["server_name"])
        self.assertEqual(cnf.server_domain_name, self.opts["server_domain_name"])
        self.assertEqual(cnf.server_port, self.opts["server_port"])
        self.assertEqual(cnf.bff_name, self.opts["bff_name"])
        self.assertEqual(cnf.bff_domain_name, self.opts["bff_domain_name"])
        self.assertEqual(cnf.bff_port, self.opts["bff_port"])

        self.assertRaises(
            IOError, cnf.set_from_file, "file-not-exist.cfg")

        self.assertRaises(
            Exception, cnf.set_from_file, "oand-invalid.cfg")

    def test_config_extended(self):
        cnf = self._config

        self.assertEqual(cnf.pid_file, "oand.pid")
        self.assertEqual(cnf.log_file, "oand.log")

class TestConfigSetFromFile(TestConfig):
    def setUp(self):
        self._config = Config()
        self._config.set_from_file("./tests/oand.cfg")

    def test_config_extended(self):
        cnf = self._config

        self.assertEqual(cnf.pid_file, self.opts["pid_file"])
        self.assertEqual(cnf.log_file, self.opts["log_file"])

class TestConfigSetFromCmdLine(TestConfigSetFromFile):
    class Options:
        pass

    def setUp(self):
        options = self.Options()
        options.__dict__ = self.opts
        self._config = Config()
        self._config.set_from_cmd_line(options)

if __name__ == '__main__':
    unittest.main()
