#!/usr/bin/env python
'''
Connection managment between nodes.

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import logging
import sys

from oan_client import OANClient

class OANNodeManager():
    # Info about my own node.
    _my_node = None

    # An dictionary with all nodes in the OAN.
    _nodes = {}

    def set_my_node(self, node):
        self._my_node = node

    def get_my_node(self):
        return self._my_node

    def add_node(self, node):
        logging.info("Add node %s" % node.uuid)
        self._nodes[node.uuid] = node
        self._remove_myself_from_nodes()

    def get_node(self, node_id):
        return self._nodes[node_id]

    def add_nodes(self, nodes):
        '''
        Merge nodes with internal nodes, replacing existing nodes.

        '''
        self._nodes.update(nodes)
        self._remove_myself_from_nodes()

    def get_nodes(self):
        return self._nodes

    @property
    def node_uuids(self):
        for node in self._nodes.itervalues():
            yield node.uuid

    def _remove_myself_from_nodes(self):
        if self.get_my_node().uuid in self._nodes:
            del(self._nodes[self.get_my_node().uuid])

    def is_online(self):
        '''
        True if any node is not expired.

        '''
        for node_id, node in self._nodes.iteritems():
            if (not node.heartbeat.is_expired()):
                return True
        return False

    def connect_to_oan(self, connection_url):
        '''
        Connect to the oand network through one known friend.

        This will only be exectued the first time the client connects to the
        oand-network.

        '''
        if len(self._nodes):
            self.check_heartbeat()

        if (not self.is_online()):
            logging.info("Connect to oan through node on %s" % (connection_url))
            for x in xrange(100):
                if (self.connect_to_node(connection_url)):
                    return
            logging.warning("Failed to connect to OAND.")

    def check_heartbeat(self):
        logging.info("Check heartbeat with %s nodes" % len(self._nodes))
        for node_id, node in self._nodes.iteritems():
            if (node.heartbeat.is_inactive()):
                # Connect to node will check heartbeat on all nodes.
                self.connect_to_node(node.connection_url)
                return
            elif (node.heartbeat.is_expired()):
                self.send_heartbeat(node)

    def connect_to_node(self, connection_url):
        try:
            remote_node = OANClient()
            remote_node.connect(connection_url)
            nodes = remote_node.get_nodes(self.get_my_node())
            logging.info("Add %d nodes from %s" % (
                              len(nodes),
                              connection_url))
            self.add_nodes(nodes)
            meta_manager().update_root_node_uuids()

            # We just recived data from this node, so it's alive.
            # TODO:
            #self.touch_last_heartbeat(node)
            self.check_heartbeat()
            return True
        except IOError as (errno, strerror):
            logging.warning(
                "Failed to connect to: " + connection_url + " " +
                "(I/O error({0}): {1}".format(errno, strerror) + ')')
        except:
            logging.warning(
                "Failed to connect to: " + connection_url +
                "Unexpected error: " + str(sys.exc_info()))
        return False

    def send_heartbeat(self, node):
        logging.debug("Send heartbeat to: " + node.name)
        try:
            remote_node = OANClient()
            remote_node.connect(node.connection_url)
            response = remote_node.send_heartbeat(self.get_my_node())
            if response['status'] == 'ok':
                self.touch_last_heartbeat(node)
        except:
            logging.warning(
                "Failed to connect to: " + node.name +
                "Unexpected error: " + str(sys.exc_info()))

    def touch_last_heartbeat(self, node):
        if node.uuid not in self._nodes:
            logging.getLogger('oand').debug(
                "Unknown node %s is touching me, adding to my nodes list." %
                vars(node))
            # When the heartbeat is expired, the next once-a-minute-scheduler
            # will ask the new node for it's node list.
            # The new node might know about nodes we are not aware of.
            node.heartbeat.set_expired()
            self.add_node(node)
        else:
            self._nodes[node.uuid].heartbeat.touch()

    def remove_expired_nodes(self):
        nodes_to_remove = []
        for node_id, node in self._nodes.iteritems():
            if (node.heartbeat.is_dead()):
                nodes_to_remove.append(node_id)
        for node_id in nodes_to_remove:
            del(self._nodes[node_id])

    def get_remote_resources(self, node_uuids, path):
        for node in self.get_node_from_uuids(node_uuids):
            logging.debug("Get resource from %s:%s." % (node_uuids, node.connection_url))
            try:
                remote = OANClient()
                remote.connect(node.connection_url)
                response = remote.get_resource(self.get_my_node(), path)
                if response['status'] == 'ok':
                    yield response
            except:
                logging.warning(
                    "Failed to connect to %s with %s: " % (node.uuid, node.connection_url),
                    "Unexpected error: " + str(sys.exc_info()))

    def get_node_from_uuids(self, node_uuids):
        '''
        Generator returning nodes with ids from node_uuids.

        '''
        for node_uuid in node_uuids:
            if node_uuid in self._nodes:
                yield self._nodes[node_uuid]
            else:
                logging.debug("%s doesn't exist in self._nodes" % node_uuid)

    def get_dbg_nodes(self):
        nodes = self._my_node.name
        for node in self.get_nodes().itervalues():
            nodes += " - "
            nodes += node.name

        return nodes
