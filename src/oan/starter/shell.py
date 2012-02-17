#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
Creating an interactive shell used to communicate with oand.

Read more about building shells in python.
    http://www.doughellmann.com/PyMOTW/cmd/

Example
$ oand
oan$ send_ping xx:xx:xx

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
import readline

from en_text import *
from oan.application import OANApplication, OANDaemon
from oan.util import log

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

    def __init__(self, config):
        self._config = config
        self.activate_cmd_history()
        cmd.Cmd.__init__(self)

    def activate_cmd_history(self):
        """
        Activate the history of commands in the oand shell.

        All old commands are stored in the home folder in the file .oand_history.

        Requires:
            sudo easy_install readline

        """
        histfile = os.path.join(os.path.expanduser("~"), ".oand_history")
        try:
            readline.read_history_file(histfile)
        except IOError:
            pass

        # Save the .oand_history file when exiting the program.
        import atexit
        atexit.register(readline.write_history_file, histfile)
        del histfile

        readline.set_completer_delims(" ")

    def completenames(self, text, *ignored):
        """
        Finds all shell commands that can be autocompleted.

        This is a copy of cmd.Cmd.completenames() with the difference that this
        functions adds a space after each command. To make more easy for the
        user to type the first argument.

        """
        dotext = 'do_'+text
        return [a[3:] + " " for a in self.get_names() if a.startswith(dotext)]

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

            # TODO: add exception to log, sys.exc_info()[0])
            log.trace("Unexpected error:")
            return self.cmdloop("")

    #
    # Command: help
    #

    def help_help(self):
        print DOC_HELP

    def do_help(self, arg):
        if arg:
            cmd.Cmd.do_help(self, arg)
        else:
            print DOC_USAGE

    def check_native(self):
        if not self._app:
            print DOC_NEED_NATIVE
            return True
        else:
            return False

    #
    # Command: quit
    #

    def help_quit(self):
        print DOC_QUIT

    def do_quit(self, line):
        print "Cleaning up and exiting."

        # Stop server if started in native mode.
        if self._app:
            self.do_stop()
        return True

    def do_EOF(self, line):
        """
        Used when piping commands to oand

        Example:
            echo "start\nstatus\nstop" | oand

        """
        return self.do_quit(line)

    #
    # Command: shell
    #
    # TODO Is this function useful or just fun and a security issue.
    #

    def help_shell(self):
        print DOC_SHELL

    def do_shell(self, line):
        print "running shell command:", line
        output = os.popen(line).read()
        print output

    #
    # Comand: start
    #

    # Modes that oan can be started in.
    # See: help_start for more info.
    SERVER_MODES = [ '--native', '--daemon']

    def help_start(self):
        print DOC_START

    def do_start(self, mode):
        if self._app:
            print "Native oand already started."
            return

        if mode == "":
            mode = '--daemon'

        if mode not in self.SERVER_MODES:
            print "Invalid start mode \"%s\"." % mode
            return

        print "Start oand in %s mode." % mode.lstrip("-")

        if mode == '--native':
            self._app = OANApplication(self._config)
            self._app.start()
        elif mode == '--daemon':
            OANDaemon(self._config).start()

    def complete_start(self, text, line, begidx, endidx):
        if not text:
            completions = self.SERVER_MODES[:]
        else:
            completions = [f + " " for f in self.SERVER_MODES
                           if f.startswith(text)]
        return completions

    #
    # Comand: stop
    #

    def help_stop(self):
        print DOC_STOP

    def do_stop(self, argument = None):
        if self._app:
            print "Stop native oand"
            self._app.stop()
            self._app = None
        else:
            print "Stop deamon oand"
            OANDaemon(self._config).stop()

    #
    # Command: restart
    #

    def help_restart(self):
        print DOC_RESTART

    def do_restart(self, argument):
        self.do_stop("")
        self.do_start("")

    #
    # Command: status
    #

    def help_status(self):
        print DOC_STATUS

    def do_status(self, argument):
        if self._app:
            print "OAN is in native mode."
        else:
            OANDaemon(self._config).status()

    #
    # Command: send_ping
    #

    def help_send_ping(self):
        print DOC_PING

    def do_send_ping(self, argument):
        if self.check_native():
            return

        print "send_ping %s (NOT IMPLEMENTED)" % argument

    #
    # Command: send_heartbeat
    #

    def help_send_heartbeat(self):
        print DOC_HEARTBEAT

    def do_send_heartbeat(self, argument):
        if self.check_native():
            return

        print "send_heartbeat %s (NOT IMPLEMENTED)" % argument

    #
    # Command: get_node_info
    #

    def help_get_node_info(self):
        print DOC_GET_NODE_INFO

    def do_get_node_info(self, argument):
        if self.check_native():
            return

        print "Node Information."
        result = self._app.get_node_info()
        print(result)
