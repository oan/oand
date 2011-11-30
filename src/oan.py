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

_data_manager = None
_meta_manager = None
_node_manager = None

def set_managers(data, meta, node):
    '''
    Set all global managers that can be used from anywhere in the app.

    '''
    global _data_manager, _meta_manager, _node_manager
    _data_manager = data
    _meta_manager = meta
    _node_manager = node
    validate()

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
    if (not _data_manager):
        raise Exception("data_manager is not valid.")

    if (not _meta_manager):
        raise Exception("meta_manager is not valid.")

    if (not _node_manager):
        raise Exception("node_manager is not valid.")
