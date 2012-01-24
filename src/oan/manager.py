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

_network = None
_database = None
_dispatch = None
_data_manager = None
_meta_manager = None
_node_manager = None

#TODO: We should make app global and use app().dispatch instead of dispatch()
def set_managers(network, database, dispatch, data, meta, node):
    '''
    Set all global managers that can be used from anywhere in the app.

    '''
    global _network, _database, _dispatch, _data_manager, _meta_manager, _node_manager

    _network = network
    _database = database
    _dispatch = dispatch
    _data_manager = data
    _meta_manager = meta
    _node_manager = node
    validate()

def network():
    return _network

def dispatch():
    return _dispatch

def database():
    return _database

def data_mgr():
    return _data_manager

def meta_mgr():
    return _meta_manager

def node_mgr():
    return _node_manager

def validate():
    '''
    Validate that all managers are set and have valid data.

    '''
    if (not _network):
        raise Exception("network is not valid.")

    if (not _database):
        raise Exception("database is not valid.")

    if (not _dispatch):
        raise Exception("dispatch is not valid.")

    if (not _data_manager):
        raise Exception("data_manager is not valid.")

    if (not _meta_manager):
        raise Exception("meta_manager is not valid.")

    if (not _node_manager):
        raise Exception("node_manager is not valid.")
