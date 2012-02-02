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

from oan.resource import OANResourceRoot
from oan import node_manager

class OANMetaManager():
    resourceRoot = None

    def __init__(self):
        self.resourceRoot = OANResourceRoot()

    def update_root_oan_ids(self):
        '''
        Update oan_ids on resourceRoot with node_manager oan_ids.

        The resourceRoot root folder should have all known oan_ids on the
        oan network.

        '''
        self.resourceRoot.get("/").oan_ids.extend(node_manager().oan_ids)

    def get(self, path):
        '''
        Returns OANResource with path.

        '''
        if not self.resourceRoot.exist(path) or self.resourceRoot.get("/").heartbeat.is_expired():
            oan_ids = self.resourceRoot.get_known_parent(path).oan_ids
            for result in node_manager().get_remote_resources(oan_ids, path):
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
    #                 if node.oan_id not in nodes:
    #                     nodes[node.oan_id] = []
    #                 nodes[node.oan_id].append(res.oan_id)

    #     for oan_ids, resUuids in nodes.iteritems():
    #         resList = self.networkNodeManager.get_resource(oan_ids, resUuids)
    #         self.resourceRoot.merge(resList)
