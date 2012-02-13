#!/usr/bin/env python
"""
Commands that are sent to the "local" dispatcher.

A command are created on node 1 and executed on node1.

"""

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from oan.manager import node_manager
from oan.util import log


class OANCommandShutdown:
    def execute(self):
        pass
