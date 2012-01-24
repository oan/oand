#!/usr/bin/env python
"""
Handling cmdline positional and optional arguments to control the oan-deamon.

"""

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import sys

from oan.config import OANConfig
from oan.util import log
from oan.starter.shell import OANShell
from argument_parser import OANArgumentParser

class OANApplicationStarter():
    """Handling cmdline positional and optional arguments to control the oan-deamon."""

    def __init__(self):
        #Get all options from command line.
        parser = OANArgumentParser()
        options = parser.parse_args()

        # Positional arguments are handled by OANShell, so delete all positional
        # arguments.
        command = options.command
        del options.command

        config = self.get_config(options)
        log.setup(
            config.syslog_level, config.stderr_level,
            config.log_level, config.log_file
        )
        config.log_options()

        # Handle positional arguments through the OANShell.
        shell = OANShell(config)

        if len(sys.argv) > 1:
            command = command[0]
            if command in ["start", "stop", "restart", "status", "help"]:
                shell.onecmd(command)
            else:
                print "Invalid shell command '%s'" % command
        else:
            shell.cmdloop()

    def get_config(self, options):
        """Create a OANConfig from file and command line options."""
        config = OANConfig()
        config.set_from_file(options.config)
        config.set_from_cmd_line(options)
        return config



