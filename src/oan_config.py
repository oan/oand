#!/usr/bin/env python
'''
Holding all configurations that can be done to oand.

Usually reading contents from a config file (oand.conf) but also possible
to initialize all data via the constructor and property members.

Domain_name/bff_domain_name should point to the public ip number,
of the oand computer node. This ip/domain are sent to remote nodes,
and they will try to connect to it later.

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.2"
__status__ = "Test"

import oan
import ConfigParser

class OANConfig(object):
    # The output verbose level 0-2
    verbose = 2 # TODO: During development it's set to 2/debug mode.

    # Config file
    config = oan.ETC_DIR + "oand.cfg"

    # Name and path of the pidfile
    pid_file = oan.VAR_DIR + "run/oand.pid"

    # Name and path of the logfile.
    log_file = oan.LOG_DIR + "oand.log"

    # This nodes unique id
    node_uuid = None

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

     # if node will act as blocked node, if True the server vill not listen to incomming connetion.
    blocked = None

    def __init__(self, node_uuid = None, node_name = None, domain_name = None, port = None,
                 bff_name = None, bff_domain_name = None, bff_port = None, blocked = False):
        '''
        Createing a Config object.

        '''
        self.node_uuid = node_uuid

        self.node_name = node_name
        self.node_domain_name = domain_name
        self.node_port = port

        self.bff_name = bff_name
        self.bff_domain_name = bff_domain_name
        self.bff_port = bff_port

        self.blocked = blocked

    def set_from_file(self, filename):
        '''
        Initialize Config from a file.

        '''
        config = ConfigParser.ConfigParser({"log-file" : oan.LOG_DIR + "oand.log"})
        config.readfp(open(filename))
        if config.has_section("oand"):
            for option in config.options("oand"):
                key = option.replace("-", "_")
                value = config.get("oand", option)
                self.set_attribute(key, value)

    def set_from_cmd_line(self, options):
        for key in options.__dict__.keys():
            value = getattr(options, key)
            if value:
                self.set_attribute(key, value)

    def set_attribute(self, key, value):
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            raise Exception(
                "Invalid config with key: " + key + " value: " + value)

    def print_options(self):
        if self.verbose == 2:
            print
            print "-- Begin ------------------"
            print "#All configuration attributes"
            print "[oand]"
            for key in self.__dict__.keys():
                value = getattr(self, key)
                print str(key) + ": " + str(value)
            print "-- End --------------------"
            print
