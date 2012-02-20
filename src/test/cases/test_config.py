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

from uuid import UUID

from test.test_case import OANTestCase
from oan.util import log
import oan
from oan.config import OANConfig, OANLogLevel, OANFileName


opts = {}
opts["config"] = "/tmp/oand.cfg"
opts["pid_file"] = "/var/run/oand.pid"
opts["log_file"] = oan.BASE_DIR + "log/unittest-oand.log"

opts['oan_id'] = "00000000-0000-dddd-0000-000000000000"
opts["node_name"] = "this-is-a-node-name"
opts["node_domain_name"] = "www.cybercow.se"
opts["node_port"] = "4000"
opts["bff_domain_name"] = "node1.cybecow.se"
opts["bff_port"] = "1337"

class TestOANConfig(OANTestCase):
    _config = None

    def setUp(self):
        self._config = OANConfig(
            opts["oan_id"],
            opts["node_name"],
            opts["node_domain_name"],
            opts["node_port"],
            opts["bff_domain_name"],
            opts["bff_port"]
        )

    def test_config(self):
        cnf = self._config
        self.assertEqual(cnf.oan_id, UUID(opts["oan_id"]))
        self.assertEqual(cnf.node_name, opts["node_name"])
        self.assertEqual(cnf.node_domain_name, opts["node_domain_name"])
        self.assertEqual(cnf.node_port, int(opts["node_port"]))
        self.assertEqual(cnf.bff_domain_name, opts["bff_domain_name"])
        self.assertEqual(cnf.bff_port, int(opts["bff_port"]))

        self.assertRaises(
            IOError, cnf.set_from_file, "file_not_exist.cfg")

        self.assertRaises(
            Exception, cnf.set_from_file, "oand_invalid.cfg")


    def test_config_extended(self):
        cnf = self._config

        self.assertEqual(cnf.pid_file, oan.VAR_DIR + "run/oand.pid")
        self.assertEqual(cnf.log_file, oan.LOG_DIR + "oand.log")


class TestOANConfigSetFromFile(OANTestCase):
    def setUp(self):
        self._config = OANConfig()
        self._config.set_from_file(oan.BASE_DIR + "src/test/cases/oand.cfg")


    def test_config_extended(self):
        cnf = self._config

        self.assertEqual(cnf.pid_file, opts["pid_file"])
        self.assertEqual(cnf.log_file, opts["log_file"])


class TestOANConfigSetFromCmdLine(OANTestCase):
    class Options:
        pass


    def setUp(self):
        options = self.Options()
        options.__dict__ = opts
        self._config = OANConfig()
        self._config.set_from_cmd_line(options)


class TestOANLogLevel(OANTestCase):


    class config(object):
        log_level1 = OANLogLevel()
        log_level2 = OANLogLevel()
        log_level3 = OANLogLevel()

        def __init__(self):
            self.log_level1 = self.log_level2 ="WARNING"


    def test_property(self):
        with self.assertRaises(Exception):
            log_level = OANLogLevel()


    def test_property(self):
        config1 = self.config()
        config2 = self.config()

        # Test default value set in OANLogLevel, non is set raise error.
        with self.assertRaises(AttributeError):
            level = config1.log_level3

        # Test default value set in config class
        self.assertEqual(config1.log_level1, log.WARNING)
        self.assertEqual(config1.log_level2, log.WARNING)
        self.assertEqual(config2.log_level1, log.WARNING)
        self.assertEqual(config2.log_level2, log.WARNING)

        # Test setting by number
        config1.log_level1 = 1
        config1.log_level2 = 2
        config2.log_level1 = 3
        config2.log_level2 = 4

        self.assertEqual(config1.log_level1, 1)
        self.assertEqual(config1.log_level2, 2)
        self.assertEqual(config2.log_level1, 3)
        self.assertEqual(config2.log_level2, 4)

        # Test setting by string
        config1.log_level1 = "DEBUG"
        config1.log_level2 = "CRITICAL"
        config2.log_level1 = "INFO"
        config2.log_level2 = "ERROR"

        self.assertEqual(config1.log_level1, log.DEBUG)
        self.assertEqual(config1.log_level2, log.CRITICAL)
        self.assertEqual(config2.log_level1, log.INFO)
        self.assertEqual(config2.log_level2, log.ERROR)

        # Test exceptions
        with self.assertRaises(ValueError):
            config1.log_level1="INVALID"

        with self.assertRaises(ValueError):
            config2.log_level1="INVALID"


class TestOANFileName(OANTestCase):

    class config(object):
        file_name1 = OANFileName("/tmp/")
        file_name2 = OANFileName("/tmp/")


        def __init__(self):
            self.file_name1 = "file1.tmp"
            self.file_name2 = "file2.tmp"


    def test_property(self):
        with self.assertRaises(Exception):
            file_name = OANFileName("/tmp")


    def test_property_on_class(self):
        config1 = self.config()
        config2 = self.config()

        # Test default value set in OANLogLevel, non is set raise error.
        with self.assertRaises(AttributeError):
            file_name = config1.file_name3

        with self.assertRaises(AttributeError):
            file_name = config1.file_name3

        # Test default value set in config class
        self.assertEqual(config1.file_name1, "/tmp/file1.tmp")
        self.assertEqual(config1.file_name2, "/tmp/file2.tmp")
        self.assertEqual(config2.file_name1, "/tmp/file1.tmp")
        self.assertEqual(config2.file_name2, "/tmp/file2.tmp")

        # Test setting by default_directory
        config1.file_name1 = "tmp1.tmp"
        config1.file_name2 = "tmp2.tmp"
        config2.file_name1 = "tmp3.tmp"
        config2.file_name2 = "tmp4.tmp"

        self.assertEqual(config1.file_name1, "/tmp/tmp1.tmp")
        self.assertEqual(config1.file_name2, "/tmp/tmp2.tmp")
        self.assertEqual(config2.file_name1, "/tmp/tmp3.tmp")
        self.assertEqual(config2.file_name2, "/tmp/tmp4.tmp")

        # Test setting by direct path.
        config1.file_name1 = "/var/log/test1.tmp"
        config1.file_name2 = "/var/log/test2.tmp"
        config2.file_name1 = "/var/log/test3.tmp"
        config2.file_name2 = "/var/log/test4.tmp"

        self.assertEqual(config1.file_name1, "/var/log/test1.tmp")
        self.assertEqual(config1.file_name2, "/var/log/test2.tmp")
        self.assertEqual(config2.file_name1, "/var/log/test3.tmp")
        self.assertEqual(config2.file_name2, "/var/log/test4.tmp")

        # Test exceptions
        with self.assertRaises(Exception):
            config1.file_name1="/xxx/xxx/xxx.tmp"

        with self.assertRaises(Exception):
            config2.file_name2="/xxx/xxx/xxx.tmp"
