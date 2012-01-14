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

import oan
from oan_config import OANConfig
from oan_argumentparser import OANArgumentParser
from oan_shell import OANShell

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

        # Handle positional arguments through the OANShell.
        shell = OANShell(self.get_config(options), parser.format_help())
        if len(sys.argv) > 1:
            shell.onecmd(' '.join(command))
        else:
            shell.cmdloop()

    def get_config(self, options):
        """Create a OANConfig from file and command line options."""
        config = OANConfig()
        config.set_from_file(options.config)
        config.set_from_cmd_line(options)
        config.print_options()
        return config
