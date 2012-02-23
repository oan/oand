#!/usr/bin/env python
"""
Represents the manager layer in OAN.

Global object instances that can be used from anywhere in the application.

Example:
from oan.manager import node_manager
from oan import manager

manager.setup(xx)
node_manager().send(xxx)
manager.shutdown()

"""

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

# Private module variables
_network = None
_database = None
_dispatcher = None
_data_manager = None
_meta_manager = None
_node_manager = None

# Exceptions raised by manager module.
class OANNetworkManagerError(Exception): pass
class OANDatabaseManagerError(Exception): pass
class OANDispatcherManagerError(Exception): pass
class OANDataManagerError(Exception): pass
class OANMetaManagerError(Exception): pass
class OANNodeManagerError(Exception): pass

def setup(data, meta, node, database, dispatcher, network):
    """
    Set all global managers that can be used from anywhere in oan.

    """
    global _network, _database, _dispatcher, _data_manager, _meta_manager, _node_manager

    _data_manager = data
    _meta_manager = meta
    _node_manager = node
    _database = database
    _dispatcher = dispatcher
    _network = network

    validate()

def shutdown():
    """
    Shutdown all managers.

    """
    global _network, _database, _dispatcher, _data_manager, _meta_manager, _node_manager

    validate()

    status = (
        _network.shutdown() and
        _dispatcher.shutdown() and
        _database.shutdown() and
        _node_manager.shutdown() and
        _meta_manager.shutdown() and
        _data_manager.shutdown()
    )

    _data_manager = None
    _meta_manager = None
    _node_manager = None
    _database = None
    _dispatcher = None
    _network = None

    return status

def network():
    return _network

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
    """
    Validate that all managers are set and have valid data.

    """
    global _network, _database, _dispatcher, _data_manager, _meta_manager, _node_manager

    if (not _network):
        raise OANNetworkManagerError()

    if (not _database):
        raise OANDatabaseManagerError()

    if (not _dispatcher):
        raise OANDispatcherManagerError()

    if (not _data_manager):
        raise OANDataManagerError()

    if (not _meta_manager):
        raise OANMetaManagerError()

    if (not _node_manager):
        raise OANNodeManagerError()

    return True
