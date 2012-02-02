#!/usr/bin/env python
'''
All configuration classes and types that can be done to oand.

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.2"
__status__ = "Test"

import os.path
import ConfigParser

import oan
from oan.util import log
from oan.util.descriptor_object import OANDescriptorObject


class OANLogLevel(OANDescriptorObject):
    """
    Represents a log_level used by oan.log or python logging.

    Can be set with both string or integer representation of a log_level
    number. Can also be any of the following alphanumerics names NONE, DEBUG,
    INFO, WARNING, ERROR, CRITICAL.

    NOTE: Classes using this class need to be of type object.

    Example:
        >>> class Config(object):
        >>>     log_level = OANLogLevel()
        >>> config = Config()
        >>> config.log_level = "DEBUG"
        >>> config.log_level = 20
        >>> print config.log_level
        20

    """
    # log_level = NOT-SET
    LOG_LEVELS = ("NONE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")

    def __get__(self, instance, objtype):
        return self.get_var(instance, "log_level")

    def __set__(self, instance, log_level):
        """
        Convert log_level to integer representation of log_level.

        """
        import logging

        str_log_level = str(log_level)
        if str_log_level.isdigit():
            num_value = int(log_level)
        else:
            log_level = log_level.upper()
            self._validate(log_level)
            num_value = getattr(logging, log_level, 100)

        self.set_var(instance, "log_level", num_value)

    def _validate(self, value):
        """Validates that the a correct log_level string are used."""
        if value not in self.LOG_LEVELS:
            raise ValueError


class OANFileName(OANDescriptorObject):
    """
    Represents a filename that can use a default directory.

    Validates that the folder of the file exists.

    NOTE: Classes using this class need to be of type object.

    Example:
        >>> class Config
        >>>     file_name1 = OANFileName("/tmp/")
        >>>     file_name2 = OANFileName("/tmp/")
        >>> config = Config()
        >>> config.file_name1 = "/file.txt"
        >>> config.file_name2 = "file.txt"
        >>> print config.file_name1
        /tmp/file.txt
        >>> print config.file_name2
        /file.txt

    """
    default_directory = None
    #file_name = NOT-SET

    def __init__(self, directory):
        OANDescriptorObject.__init__(self)
        if directory[-1] != "/":
            raise Exception("Directory must end with / (%s)" % directory)

        self.default_directory = directory

    def __get__(self, instance, owner):
        return self.get_var(instance, "file_name")

    def __set__(self, instance, path):
        if path[0] == "/":
            self.set_var(instance, "file_name", path)
        else:
            self.set_var(instance, "file_name", self.default_directory + path)

        self.validate(instance)

    def validate(self, instance):
        """Validate that folder for path exists"""
        path = self.get_var(instance, "file_name")
        directory = path.rpartition("/")[0] + "/"
        if not os.path.exists(directory):
            raise Exception("Directory %s doesn't exist." % directory)


class OANConfig(object):
    """
    Holding all configurations that can be done to oand.

    Usually reading contents from a config file (oand.conf) but also possible
    to initialize all data via the constructor and property members.

    Domain_name/bff_domain_name should point to the public ip number,
    of the oand computer node. This ip/domain are sent to remote nodes,
    and they will try to connect to it later.

    """
    # Too many instance attributes
    # pylint: disable=R0902
    #   This config class are allowed to have many attributes.

    # Config file
    config = OANFileName(oan.ETC_DIR)

    # Name and path of the pidfile
    pid_file = OANFileName(oan.VAR_DIR)

    # log-level of log messages that should be sent to syslog.
    # The log level can be any of NONE, DEBUG, INFO, WARNING, ERROR, CRITICAL.
    syslog_level = OANLogLevel()

    # log-level of log messages that should be sent to stderr.
    # The log level can be any of NONE, DEBUG, INFO, WARNING, ERROR, CRITICAL.
    stderr_level = OANLogLevel()

    # log-level of log messages that should be sent to log file.
    # The log level can be any of NONE, DEBUG, INFO, WARNING, ERROR, CRITICAL.
    log_level = OANLogLevel()

    # Defines in which file, logs should be stored to if log-level is higher
    # than none.
    log_file = OANFileName(oan.LOG_DIR)

    # This nodes unique id
    oan_id = None

    # The name of the server oand is running on. This has no connection
    # to the hostname in the OS, it's just for reference.
    node_name = None

    # The public ip number or domain name of this oand node.
    node_domain_name = None

    # The tcp/ip port that is open for connection.
    node_port = None

    # Best Friend Forever Node. The first node to connect to, which will
    # give you access and knowledge to the whole network.
    bff_name = None
    bff_domain_name = None
    bff_port = None

    # This node can't be reached from internet through firewall.
    blocked = None

    # if node will act as blocked node, if True the server vill not listen to
    # incomming connetion.
    blocked = None

    # Too many arguments
    # pylint: disable=R0913
    #   This config class are allowed to be set with many arguments.

    def __init__(
        self,
        oan_id=None, node_name=None, domain_name=None, port=None,
        bff_name=None, bff_domain_name=None, bff_port=None,
        blocked=False
    ):
        '''
        Createing a Config object.

        '''
        self.config = "oand.cfg"
        self.pid_file = "run/oand.pid"
        self.syslog_level = "NONE"
        self.stderr_level = "NONE"
        self.log_level = "DEBUG"
        self.log_file = "oand.log"

        self.oan_id = oan_id

        self.node_name = node_name
        self.node_domain_name = domain_name
        self.node_port = port

        self.bff_name = bff_name
        self.bff_domain_name = bff_domain_name
        self.bff_port = bff_port

        self.blocked = blocked

    def set_from_file(self, filename):
        """Initialize config from a file."""
        config = ConfigParser.ConfigParser(
            {"log-file": oan.LOG_DIR + "oand.log"}
        )
        config.readfp(open(filename))
        if config.has_section("oand"):
            for option in config.options("oand"):
                key = option.replace("-", "_")
                value = config.get("oand", option)
                self.set_attribute(key, value)

    def set_from_cmd_line(self, options):
        """Initialize config from a command line argParser.options."""
        for key in options.__dict__.keys():
            value = getattr(options, key)
            if value:
                self.set_attribute(key, value)

    def set_attribute(self, key, value):
        """Set an attribute comming from a string."""
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            raise Exception(
                "Invalid config with key: " + key + " value: " + value)

    def log_options(self):
        """Print all internal variables. (Used for debug purpose)"""
        log.debug("-------- ALL CONFIG OPTIONS ---------")
        log.debug("[oand]")
        for key in self.__dict__.keys():
            value = getattr(self, key)
            log.debug("\t%s: %s" % (key, value))
        log.debug("-------------------------------------")
