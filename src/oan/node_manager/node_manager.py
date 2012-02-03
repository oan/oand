#!/usr/bin/env python
"""
"""
__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from threading import Lock

from oan.heartbeat import OANHeartbeat
from oan.manager import network, database
from oan.util import log
from oan.dispatcher.message import OANMessageNodeSync, OANMessageHeartbeat, OANMessageRelay
from oan.network.network_node import OANNetworkNode
from oan.network.command import NetworksCommandConnectToNode
from oan.util.decorator.synchronized import synchronized

class OANNodeManager():
    _config = None

    # A dictionary with all nodes in the OAN.
    _nodes = {}

    # Info about my own node.
    _my_node = None

    # Synchronize the node instance when accessed by several threads.
    _lock = None


    def __init__(self, config):
        self._config = config
        self._lock = Lock()


    @synchronized
    def load(self):
        """ Load all nodes in to memory and set _my_node"""
        for node in database().select_all(OANNetworkNode):
            self._update_node(node)

        if self._config.oan_id in self._nodes:
            self._set_my_node(self._nodes[self._config.oan_id])
        else:
            self._create_my_node()

    @synchronized
    def store(self):
        database().replace_all(self._nodes.values())


    @synchronized
    def create_node(self, oan_id, host, port, blocked):
        return self._create_node(oan_id, host, port, blocked)


    @synchronized
    def get_my_node(self):
        return self._my_node


    @synchronized
    def get_node(self, oan_id):
        return self._nodes[oan_id]

    '''
    #TODO: remove dead nodes in database
    def remove_dead_nodes(self):
        for n in self._nodes.values():
            if n.oan_id != self._my_node.oan_id:
                if n.heartbeat.is_dead():
                    del self._nodes[n.oan_id]

    #TODO: maybe should send heartbeat to blocked nodes to test. once a week or so.
    def send_heartbeat(self):
        heartbeat = OANMessageHeartbeat.create(self._my_node)
        for n in self._get_nodes():
            if not n.blocked:
                self.send(n.oan_id, heartbeat)

    #TODO sync ony with open nodes
    def send_node_sync(self):
        node_sync = OANMessageNodeSync.create()
        for n in self._get_nodes():
            if n.oan_id != self._my_node.oan_id:
                self.send(n.oan_id, node_sync)
    '''

    #TODO: not all message should be relay
    def send(self, oan_id, message):
        log.debug("oan_id: %s, message: %s" % (oan_id, str(message)))

        if (oan_id in self._nodes):
            node = self._nodes[oan_id]
            if node.blocked and self._my_node.blocked:
                self.relay(oan_id, message)
            else:

                #try:
                node.out_queue.put(message, False)
                #    self._my_node.statistic.out_queue_inc()
                #except:
                #    log.info("Queue full cleaning up")
                #    save_messages = []
                #    while True:
                #        try:
                #            message_on_queue = node.out_queue.get(False)
                #            if message_on_queue.ttl:
                #                save_message.append(message_on_queue)
                #            else:
                #                log.info("remove %s" % message_on_queue)
                #        except:
                #            log.info("empty cleaning up")
                #            break

                    #TODO check if all save_messages culd be put back on queue.
                 #   for m in save_messages:
                 #       node.out_queue.put(m)

                  #  node.out_queue.put(message)

                if node.is_disconnected():
                    network().execute(NetworksCommandConnectToNode.create(node))
        else:
            log.info("OANNodeManager:Error node is missing %s" % oan_id)
            log.info(self._nodes)


    #TODO: find good relay nodes.
    def relay(self, destination_uuid, message):
        relay = OANMessageRelay.create(self._my_node.oan_id, destination_uuid, message)
        for relay_node in self._nodes.values():
            if relay_node.oan_id != self._my_node.oan_id:
                if not relay_node.blocked:
                    log.info("Relay %s to [%s] throw [%s]" % (message.__class__.__name__, destination_uuid, relay_node.oan_id))
                    self.send(relay_node.oan_id, relay)
                    return

        log.info("OANNodeManager:Error can not relay message no relay node found")

    def shutdown(self):
        pass


    def get_nodes(self):
        """
        Returns all nodes that is not expired, this i use for sending
        heartbeat and node_sync etc.

        DISCUSS: make heartbeat._is_touch public and send in a parameter
                 heartbeat.EXPIRED_MIN to this function get_nodes(self, min = OANHeartbeat.EXPIRED_MIN):

                 make heartbeat.EXPIRED_MIN to a static variable.

        """

        print self._nodes
        ret = []
        for n in self._nodes.values():
            if n.oan_id != self._my_node.oan_id:
                ret.append(n)

        return ret

    def dump(self):
        log.info("------ dump begin ------")
        for n in self._nodes.values():
            log.info("\t %s" % n)
        log.info("------ dump end ------")


    def _create_node(self, oan_id, host, port, blocked):
        if oan_id in self._nodes:
            node = self._nodes[oan_id]
            node.update(host = host, port = port,
                        blocked = blocked)
        else:
            node = OANNetworkNode.create(oan_id, host, port, blocked)
            self._nodes[oan_id] = node

        return node

    def _update_node(self, node):
        if node.oan_id in self._nodes:
            n = self._nodes[node.oan_id]
            n.update(host = node.host, port = node.port,
                        blocked = node.blocked)
        else:
            self._nodes[node.oan_id] = node

    def _set_my_node(self, node):
        if self._my_node is None:
            node.update(
                host = self._config.node_domain_name,
                port = int(self._config.node_port),
                blocked = self._config.blocked)

            self._my_node = node
        else:
            log.info("OANNodeManager:Error my node is already set")


    def _create_my_node(self):
        if self._my_node is None:
            node = self._create_node(
                self._config.oan_id,
                self._config.node_domain_name,
                int(self._config.node_port),
                self._config.blocked
            )

            self._my_node = node
        else:
            log.info("OANNodeManager:Error my node is already set")


