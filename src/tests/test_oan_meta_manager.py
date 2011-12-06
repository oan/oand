#!/usr/bin/env python
'''
Test cases for OANMetaManager

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

# from twisted.trial import unittest
# import logging

# from oan_resource import *
# from oand import OANDaemon
# from oan_config import OANConfig
# from oan_meta_manager import OANMetaManager
# from oan_node_manager import OANNodeManager
# from oan_network_node import OANNetworkNode

# class TestOANMetaManager(unittest.TestCase):

#     def start_logging(self):
#         # Setup logging
#         ch1 = logging.handlers.RotatingFileHandler(
#             "/tmp/oan-test.log", maxBytes=2000000, backupCount=100)
#         ch1.setLevel(logging.DEBUG)
#         formatter = logging.Formatter(
#             '%(asctime)s - oand (%(process)d) - %(message)s')
#         ch1.setFormatter(formatter)
#         logging.getLogger().addHandler(ch1)

#     def create_network_node_manager(self):
#         network_node_manager = OANNodeManager()

#         network_node_manager.set_my_node(OANNetworkNode(
#             'self-node-1',
#             'self-node',
#             'localhost',
#             '3000'
#         ))

#         network_node_manager.connect_to_oan("localhost:4000")

#         return network_node_manager

#     def setUp(self):
#         self.start_logging()
#         network_node_manager = self.create_network_node_manager()

#         self.manager = OANMetaManager()

#     def test_all(self):
#         #self.manager.get('/music/rock/queen.mp3')
#         #self.manager.get('/music/')
#         self.manager.get('/')

#         #self.manager.refresh()

# if __name__ == '__main__':
#     unittest.main()
