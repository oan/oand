#!/usr/bin/env python

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.2"
__status__ = "Test"

import ConfigParser

class Config(object):
    '''
    Holding all configurations that can be done to oand.

    Usually reading contents from a config file (oand.conf) but also possible
    to initialize all data via the constructor and property members.

    Domain_name/bff_domain_name should point to the public ip number,
    of the oand computer node. This ip/domain are sent to remote nodes,
    and they will try to connect to it later.

    '''

    # The output verbose level 0-2
    verbose = 2 # TODO: During development it's set to 2/debug mode.

    # Config file
    config = "oand.cfg"

    # Name and path of the pidfile
    pid_file = "oand.pid"

    # Name and path of the logfile.
    log_file = "oand.log"

    # The name of the server oand is running on. This has no connection
    # to the hostname in the OS, it's just for reference.
    server_name = None

    # The public ip number or domain name of this oand node.
    server_domain_name = None

    # The tcp/ip port that is open for connection.
    server_port = None

    # Best Friend Forever Node. The first node to connect to, which will
    # give you access and knowledge to the whole network.
    bff_name = None
    bff_domain_name = None
    bff_port = None

    def __init__(self, server_name = None, domain_name = None, port = None,
                 bff_name = None, bff_domain_name = None, bff_port = None):
        '''
        Createing a Config object.

        '''
        self.server_name = str(server_name)
        self.server_domain_name = str(domain_name)
        self.server_port = str(port)

        self.bff_name = str(bff_name)
        self.bff_domain_name = str(bff_domain_name)
        self.bff_port = str(bff_port)

    def set_from_file(self, filename):
        '''
        Initialize Config from a file.

        '''
        config = ConfigParser.ConfigParser({"log-file" : "oand.log"})
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
