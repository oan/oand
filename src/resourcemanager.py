#!/usr/bin/env python
'''


'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from resources import *
import OANSerializer




class ResourceManager():
    resourceRoot = None
    networkNodeManager = None

    def __init__(self, networkNodeManager):
        self.resourceRoot = ResourceRoot()
        self.networkNodeManager = networkNodeManager
        self.resourceRoot.get("/").node_uuids.extend(networkNodeManager.node_uuids)

    def get(self, path):
        '''
        Returns OANResource with path.

        '''
        if not self.resourceRoot.exist(path) or self.resourceRoot.get("/").heartbeat.is_expired():
            node_uuids = self.resourceRoot.get_known_parent(path).node_uuids
            for result in self.networkNodeManager.get_remote_resources(node_uuids, path):
                print OANSerializer.decode(result)
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
