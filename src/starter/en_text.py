#!/usr/bin/env python
"""
All texts in english that are used by the oand starter (shell/cmdline)

"""

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import oan

DOC_INTRO = """Open Archive Network Shell - Version %s

Type:  'help' for help with commands
       'quit' to quit
""" % __version__

DOC_USAGE = """
oand [options] [commands]

commands:
  help           - print help
  quit           - quit this interactive shell
  start          - start OAN as a deamon.
  stop           - stop OAN as a deamon.
  restart        - restart OAN as a deamon.
  start-native   - start OAN in native mode.
  send-ping      - send a ping to a remote node.
  send-heartbeat - send a heartbeat to a remote node."""

DOC_HELP = """
  NAME
    help - print help

  SYNOPSIS
    help [<command>]

  DESCRIPTION
    Prints global help or command specific help.

  OPTIONS
    <command>        name of command
"""

DOC_QUIT = """
  NAME
    quit - quit this interactive shell

  SYNOPSIS
    quit
"""

DOC_SHELL = """
  NAME
    shell - run a shell command

  SYNOPSIS
    shell [command]
    ! [command]

  DESCRIPTION
    Used to execute any shell command from the oand shell. This can be done
    both with for examle "shell ls -alvh" and "! ls -alvh"

  OPTIONS
    [command]

"""


DOC_START = """
  NAME
    start - start OAN as a deamon.

  SYNOPSIS
    start

  DESCRIPTION
    Start Open Archive Network as a deamon.

  OPTIONS
    <command>        name of shell command
"""

DOC_STOP = """
  NAME
    stop - stop OAN as a deamon.

  SYNOPSIS
    stop

  DESCRIPTION
    Stop Open Archive Network as a deamon.

  OPTIONS
    None
"""

DOC_RESTART = """
  NAME
    restart - restart OAN as a deamon.

  SYNOPSIS
    restart [--server-name]

  DESCRIPTION
    Retart Open Archive Network as a deamon.

  OPTIONS
    None
"""

DOC_STATUS = """
  NAME
    status - status of OAN deamon.

  SYNOPSIS
    status

  DESCRIPTION
    Status of Open Archive Network deamon.

  OPTIONS
    None
"""

DOC_START_NATIVE = """
  NAME
    start-native - start OAN in native mode.

  SYNOPSIS
    start-native

  DESCRIPTION
    Start Open Archive Network in native mode. This means that OAN will use
    the same process as the starter and no deamon will be used.

    What this really means is that error messages and other things written
    to stdout and stderr will be displayed to the user. This can be really
    useful when debugging the application.

  OPTIONS
    None
"""

DOC_PING = """
NAME
    send-ping - send a ping to a remote node.

SYNOPSIS
    send-ping <node-id>

DESCRIPTION
    Send a ping message to a remote OAN node.

    This message can only be used in native mode.

OPTIONS
    <node-id>         UUID to a remote node.
"""

DOC_HEARTBEAT = """
NAME
    send-heartbeat - send a heartbeat to a remote node.

SYNOPSIS
    send-heartbeat <node-id>

DESCRIPTION
    Send a heartbeat message to a remote OAN node.

    This message can only be used in native mode.

OPTIONS
    <node-id>         UUID to a remote node.
"""
