#!/usr/bin/env python
'''
Handles metadata for the filesystem/resources.

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from oan_resource import OANResourceRoot
from oan import node_manager

class OANMetaManager():
    resourceRoot = None

    def __init__(self):
        self.resourceRoot = OANResourceRoot()

    def update_root_node_uuids(self):
        '''
        Update node_uuids on resourceRoot with node_manager node_uuids.

        The resourceRoot root folder should have all known node_uuids on the
        oan network.

        '''
        self.resourceRoot.get("/").node_uuids.extend(node_manager().node_uuids)

    def get(self, path):
        '''
        Returns OANResource with path.

        '''
        if not self.resourceRoot.exist(path) or self.resourceRoot.get("/").heartbeat.is_expired():
            node_uuids = self.resourceRoot.get_known_parent(path).node_uuids
            for result in node_manager().get_remote_resources(node_uuids, path):
                pass
                #self.resourceRoot.set(path, res)

        return self.resourceRoot.get(path)

    # def refresh(self):
    #     '''
    #     Will sync all info in the ResourceRoot with all other nodes.

    #     Should be executed every X minute.

    #     '''
    #     nodes = {}
    #     for res in self.resourceRoot.resources:
    #         if res.heartbeat.is_expired()
    #             for node in res.nodeuuids:
    #                 if node.uuid not in nodes:
    #                     nodes[node.uuid] = []
    #                 nodes[node.uuid].append(res.uuid)

    #     for node_uuids, resUuids in nodes.iteritems():
    #         resList = self.networkNodeManager.get_resource(node_uuids, resUuids)
    #         self.resourceRoot.merge(resList)
