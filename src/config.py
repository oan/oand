#!/usr/bin/env python
'''
Holding all configurations that can be done to oand.

Usually reading contents from a config file (oand.conf) but also possible
to initialize all data via the constructor.

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import ConfigParser

class Config():
    # The name of the server oand is running on. This has no connection
    # to the hostname in the OS.
    _server_name = None

    # The ip number or domain name of this oand node.
    _server_domain_name = None

    # The tcp/ip port that is open for connection.
    _server_port = None

    # Best Friend Forever Node. The first node to connect to, which will
    # give you access and knowledge to the whole network.
    _bff_name = None
    _bff_domain_name = None
    _bff_port = None

    def __init__(self, server_name, domain_name, port,
                   bff_name = None, bff_domain_name = None, bff_port = None):
        self._server_name = server_name
        self._server_domain_name = domain_name
        self._server_port = port

        self._bff_name = bff_name
        self._bff_domain_name = bff_domain_name
        self._bff_port = bff_port

    @classmethod
    def from_filename(cls, filename):
        "Initialize Config from a file"
        config = ConfigParser.ConfigParser()
        config.readfp(open(filename))

        return cls(
          cls.get_from_config(config, "oand", "server-name"),
          cls.get_from_config(config, "oand", "server-domain-name"),
          cls.get_from_config(config, "oand", "server-port"),
          cls.get_from_config(config, "oand", "bff-name"),
          cls.get_from_config(config, "oand", "bff-domain-name"),
          cls.get_from_config(config, "oand", "bff-port")
        )

    @staticmethod
    def get_from_config(config, section, option):
        if config.has_section(section) and config.has_option(section, option):
            return config.get(section, option)
        else:
            return None

    def get_server_name(self):
        return self._server_name

    def get_server_domain_name(self):
        return self._server_domain_name

    def get_server_port(self):
        return self._server_port

    def get_bff_name(self):
        return self._bff_name

    def get_bff_domain_name(self):
        return self._bff_domain_name

    def get_bff_port(self):
        return self._bff_port