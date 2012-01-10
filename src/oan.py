#!/usr/bin/env python
'''
Global object instances that can be used from anywhere in the application.

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import os
import sys

_loop = None
_database = None
_dispatcher = None
_data_manager = None
_meta_manager = None
_node_manager = None

# OAN application root folder.
BASE_DIR = os.path.abspath(__file__ + "/../../") + "/"

# All variable data.
VAR_DIR = BASE_DIR + "var/"

# Etc (config) files.
ETC_DIR = BASE_DIR + "etc/"

# Log files
LOG_DIR = BASE_DIR + "log/"

#TODO: We should make app global and use app().dispatcher instead of dispatcher()
def set_managers(loop, database, dispatcher, data, meta, node):
    '''
    Set all global managers that can be used from anywhere in the app.

    '''
    global _loop, _database, _dispatcher, _data_manager, _meta_manager, _node_manager

    _loop = loop
    _database = database
    _dispatcher = dispatcher
    _data_manager = data
    _meta_manager = meta
    _node_manager = node
    validate()

def loop():
    return _loop

def dispatcher():
    return _dispatcher

def database():
    return _database

def data_manager():
    return _data_manager

def meta_manager():
    return _meta_manager

def node_manager():
    return _node_manager

def validate():
    '''
    Validate that all managers are set and have valid data.

    '''
    if (not _loop):
        raise Exception("loop is not valid.")

    if (not _database):
        raise Exception("database is not valid.")

    if (not _dispatcher):
        raise Exception("dispatcher is not valid.")

    if (not _data_manager):
        raise Exception("data_manager is not valid.")

    if (not _meta_manager):
        raise Exception("meta_manager is not valid.")

    if (not _node_manager):
        raise Exception("node_manager is not valid.")

if __name__ == '__main__':
    print "__file__: " + __file__
    print "BASE_DIR: " + BASE_DIR
    print "VAR_DIR: "  + VAR_DIR
    print "ETC_DIR: "  + ETC_DIR
    print "LOG_DIR: "  + LOG_DIR
