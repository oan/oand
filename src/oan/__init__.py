"""
Constanst available via package oan.

"""

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import os

# OAN application root folder.
BASE_DIR = os.path.abspath(__file__).rsplit('/', 3)[0] + "/"

# All variable data.
VAR_DIR = BASE_DIR + "var/"

# Etc (config) files.
ETC_DIR = BASE_DIR + "etc/"

# Log files
LOG_DIR = BASE_DIR + "log/"
