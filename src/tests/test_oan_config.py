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

import oan
from oan_config import OANConfig

class TestOANConfig(unittest.TestCase):
    _config = None

    # Options
    opts = {}
    opts["verbose"] = 5
    opts["config"] = "/tmp/oand.cfg"
    opts["pid_file"] = "/tmp/oand.pid"
    opts["log_file"] = "/tmp/oand.log"

    opts['node_uuid'] = "1"
    opts["node_name"] = "this-is-a-node-name"
    opts["node_domain_name"] = "www.cybercow.se"
    opts["node_port"] = "4000"
    opts["bff_name"] = "LeetNode"
    opts["bff_domain_name"] = "node1.cybecow.se"
    opts["bff_port"] = "1337"

    def setUp(self):
        self._config = OANConfig(
            self.opts["node_uuid"],
            self.opts["node_name"],
            self.opts["node_domain_name"],
            self.opts["node_port"],
            self.opts["bff_name"],
            self.opts["bff_domain_name"],
            self.opts["bff_port"]
        )

    def test_config(self):
        cnf = self._config
        self.assertEqual(cnf.node_uuid, self.opts["node_uuid"])
        self.assertEqual(cnf.node_name, self.opts["node_name"])
        self.assertEqual(cnf.node_domain_name, self.opts["node_domain_name"])
        self.assertEqual(cnf.node_port, self.opts["node_port"])
        self.assertEqual(cnf.bff_name, self.opts["bff_name"])
        self.assertEqual(cnf.bff_domain_name, self.opts["bff_domain_name"])
        self.assertEqual(cnf.bff_port, self.opts["bff_port"])

        self.assertRaises(
            IOError, cnf.set_from_file, "file_not_exist.cfg")

        self.assertRaises(
            Exception, cnf.set_from_file, "oand_invalid.cfg")

    def test_config_extended(self):
        cnf = self._config

        self.assertEqual(cnf.pid_file, oan.VAR_DIR + "run/oand.pid")
        self.assertEqual(cnf.log_file, oan.LOG_DIR + "oand.log")

class TestOANConfigSetFromFile(TestOANConfig):
    def setUp(self):
        self._config = OANConfig()
        self._config.set_from_file(oan.BASE_DIR + "src/tests/oand.cfg")

    def test_config_extended(self):
        cnf = self._config

        self.assertEqual(cnf.pid_file, self.opts["pid_file"])
        self.assertEqual(cnf.log_file, self.opts["log_file"])

class TestOANConfigSetFromCmdLine(TestOANConfigSetFromFile):
    class Options:
        pass

    def setUp(self):
        options = self.Options()
        options.__dict__ = self.opts
        self._config = OANConfig()
        self._config.set_from_cmd_line(options)

if __name__ == '__main__':
    unittest.main()
