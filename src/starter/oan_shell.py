#!/usr/bin/env python
"""
Creating an interactive shell used to communicate with oand.

Read more about building shells in python.
    http://www.doughellmann.com/PyMOTW/cmd/

Example
oand ping xx:xx:xx

"""

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import sys
import cmd
import os

import oan
from en_text import *
from oan_config import OANConfig
from oan_application import OANApplication, OANDaemon

class OANShell(cmd.Cmd):
    """Creating an interactive shell used to communicate with oand."""

    # Displayed when entering the shell
    intro = DOC_INTRO

    # Displayed before the prompt.
    prompt = 'oan$ '

    # OANConfig initialized from cmdline and config file.
    config = None

    # Help text displayed when typing "oand help"
    help = None

    def __init__(self, config, help):
        self.config = config
        cmd.Cmd.__init__(self)
        self.help = help

    def emptyline(self):
        """
        Don't run the last command again automatically.

        The default beaviour of cmd.Cmd when no command is specified on the cmd-
        line is to execute the last command. This functionality is disabled.

        """
        return False

    def cmdloop(self, intro=None):
        """
        The big loop in the shell.

        Overiding to handle keyboard interrupt (ctrl-c)

        """
        try:
            return cmd.Cmd.cmdloop(self, intro)
        except KeyboardInterrupt:
            print
            return self.do_quit(None)
        except:
            raise

    def help_help(self):
        print DOC_HELP

    def help_quit(self):
        print DOC_QUIT

    def help_shell(self):
        print DOC_SHELL

    def help_start(self):
        print DOC_START

    def help_stop(self):
        print DOC_STOP

    def help_restart(self):
        print DOC_RESTART

    def help_status(self):
        print DOC_STATUS

    def help_start_native(self):
        print DOC_START_NATIVE

    def help_send_ping(self):
        print DOC_PING

    def help_send_heartbeat(self):
        print DOC_HEARTBEAT

    def do_help(self, arg):
        if arg:
            cmd.Cmd.do_help(self, arg)
        else:
            print self.help

    def do_EOF(self, line):
        """
        Used when piping commands to oand

        Example:
            echo "start\nstatus\nstop" | oand

        """
        return self.do_quit(line)

    def do_quit(self, line):
        print "Cleaning up and exiting."
        return True

    # TODO Is this function useful or just fun and a security issue.
    def do_shell(self, line):
        print "running shell command:", line
        output = os.popen(line).read()
        print output

    def do_start(self, argument):
        OANDaemon(self.config).start()

    def do_stop(self, argument):
        OANDaemon(self.config).stop()

    def do_restart(self, argument):
        OANDaemon(self.config).restart()

    def do_status(self, argument):
        OANDaemon(self.config).status()

    def do_start_native(self, argument):
        OANApplication(self.config).run()

    def do_send_ping(self, argument):
        print "send_ping %s (NOT IMPLEMENTED)" % argument

    def do_send_heartbeat(self, argument):
        print "send_heartbeat %s (NOT IMPLEMENTED)" % argument
