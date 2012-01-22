#!/usr/bin/env python
"""
Defines and parses all cmd line options.

"""

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from argparse import ArgumentParser, RawTextHelpFormatter

import oan
from en_text import *

class OANHelpFormatter(RawTextHelpFormatter):
    """Change indentation of optional arguments help text."""
    def __init__(self, prog):
        RawTextHelpFormatter.__init__(self, prog, 2, 40, 80)

    def add_usage(self, usage, actions, mutually_exclusive_groups):
        pass

class OANArgumentParser(ArgumentParser):
    """Defines and parses all cmd line options."""

    def __init__(self):
        ArgumentParser.__init__(
            self,
            usage = "oand [options] [commands]",
            description = DOC_USAGE_TERMINAL,
            version = "Open Archive Network Shell - Version %s" % __version__,
            add_help = True,
            formatter_class = OANHelpFormatter,
            conflict_handler='resolve'
        )

        self.add_arguments()
        self.add_commands()

    def add_arguments(self):
        self.add_argument(
            "-v", "--verbose", action="store_const", const=2, dest="verbose",
            help="Show more output."
        )

        self.add_argument(
            "-q", "--quiet", action="store_const", const=0, dest="verbose",
            help="show no output."
        )

        self.add_argument(
            "--server-name", metavar="NAME",
            help="the server name."
        )

        self.add_argument(
            "--server-domain-name", metavar="NAME",
            help="the server domain name or ip."
        )

        self.add_argument(
            "--server-port", metavar="PORT", type=int,
            help="the server port number."
        )

        self.add_argument(
            "--bff-name", metavar="NAME",
            help="the bff server name."
        )

        self.add_argument(
            "--bff-domain-name", metavar="NAME",
            help="the bff server domain name or ip."
        )

        self.add_argument(
            "--bff-port", metavar="PORT", type=int,
            help="the bff server port number."
        )

        self.add_argument(
            "--defaults-extra-file", metavar="FILE",
            dest="config", default = oan.ETC_DIR + "oand.cfg",
            help="the name of the config file."
        )

        self.add_argument(
            "--pid-file", metavar="FILE",
            help="the pid-file path."
        )

        self.add_argument(
            "--syslog-level", metavar="TYPE",
            help="log-level of log messages that should be sent to syslog."
        )

        self.add_argument(
            "--stderr-level", metavar="TYPE",
            help="log-level of log messages that should be sent to stderr."
        )

        self.add_argument(
            "--log-level", metavar="TYPE",
            help="log-level of log messages that should be sent to log file."
        )

        self.add_argument(
            "--log-file", metavar="FILE",
            help="the log-file path."
        )

    def add_commands(self):
        """
        This is a dummy command, needed to remove error message.

        All positional arguments are handled by OANShell

        """
        self.add_argument(
            "command", nargs='*',
            help="action that should be performed."
        )
