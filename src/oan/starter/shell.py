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
import traceback

from en_text import *
from oan.config import OANConfig
from oan.application import OANApplication, OANDaemon

class OANShell(cmd.Cmd):
    """Creating an interactive shell used to communicate with oand."""

    # Displayed when entering the shell
    intro = DOC_INTRO

    # Displayed before the prompt.
    prompt = 'oan$ '

    # OANConfig initialized from cmdline and config file.
    _config = None

    # Application object when started in native mode.
    _app = None

    # Help text displayed when typing "oand help"
    _help = None

    def __init__(self, config, help):
        self._config = config
        cmd.Cmd.__init__(self)
        self._help = help

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
        except Exception as e:
            print e
            print "Unexpected error:", sys.exc_info()[0]
            traceback.print_tb(sys.exc_info()[2])
            return self.cmdloop("")

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

    def help_get_node_info(self):
        print DOC_GET_NODE_INFO

    def do_help(self, arg):
        if arg:
            cmd.Cmd.do_help(self, arg)
        else:
            print self._help

    def print_need_native(self):
        print DOC_NEED_NATIVE

    def do_EOF(self, line):
        """
        Used when piping commands to oand

        Example:
            echo "start\nstatus\nstop" | oand

        """
        return self.do_quit(line)

    def do_quit(self, line):
        print "Cleaning up and exiting."

        # Stop server if started in native mode.
        if self._app:
            self.do_stop()
        return True

    # TODO Is this function useful or just fun and a security issue.
    def do_shell(self, line):
        print "running shell command:", line
        output = os.popen(line).read()
        print output

    def do_start(self, argument):
        OANDaemon(self._config).start()

    def do_stop(self, argument = None):
        if self._app:
            print "Stop native oand"
            self._app.stop()
            self._app = None
        else:
            print "Stop deamon oand"
            OANDaemon(self._config).stop()

    def do_restart(self, argument):
        OANDaemon(self._config).restart()

    def do_status(self, argument):
        OANDaemon(self._config).status()

    def do_start_native(self, argument):
        if not self._app:
            print "Start native oand"
            self._app = OANApplication(self._config)
            self._app.run()
        else:
            print "Native oand already started."

    def do_send_ping(self, argument):
        print "send_ping %s (NOT IMPLEMENTED)" % argument

    def do_send_heartbeat(self, argument):
        print "send_heartbeat %s (NOT IMPLEMENTED)" % argument

    def do_get_node_info(self, argument):
        if self._app:
            print "Node Information."
            result = self._app.get_node_info()
            print(result)
        else:
            self.print_need_native()
