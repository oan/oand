# __init__.py

import os

# OAN application root folder.
BASE_DIR = os.path.abspath(__file__).rsplit('/', 3)[0] + "/"

# All variable data.
VAR_DIR = BASE_DIR + "var/"

# Etc (config) files.
ETC_DIR = BASE_DIR + "etc/"

# Log files
LOG_DIR = BASE_DIR + "log/"

# todo: Should be moved to dispatcher??
#from manager import *
