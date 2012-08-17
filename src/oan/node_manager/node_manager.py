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
from Queue import Full

from oan.heartbeat import OANHeartbeat
from oan.manager import network, database, dispatcher
from oan.util import log
from oan.dispatcher.message import OANMessageRelay
from oan.async.network_node import OANNetworkNode
from oan.async.command import NetworksCommandConnectToNode
from oan.async.bridge import OANBridgeAuth
from oan.util.network import get_local_host

from oan.node_manager.command import OANCommandCleanOutQueue

from oan.util.decorator.synchronized import synchronized

class OANNodeManager():
    _config = None

    # A dictionary with all nodes in the OAN.
    _nodes = None

    # Info about my own node.
    _my_node = None

    # Synchronize the node_manager when accessed by several threads.
    _lock = None


    def __init__(self, config):
        self._config = config
        self._auth = OANBridgeAuth.create(
            version = "oand v1.0",
            oan_id = config.oan_id,
            host = get_local_host(),
            port = config.node_port,
            blocked = config.blocked)

        self._nodes = {}
        self._lock = Lock()


    @synchronized
    def load(self):
        """ Load all nodes in to memory and set _my_node"""
        for node in database().select_all(OANNetworkNode):
            self._add_node(node)

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
    def get_auth(self):
        return self._auth

    @synchronized
    def get_node(self, oan_id):
        if oan_id in self._nodes:
            return self._nodes[oan_id]

        return None

    @synchronized
    def exist_node(self, oan_id):
        return oan_id in self._nodes

    @synchronized
    def get_nodes(self, heartbeat_state = None):
        """
        Returns all nodes that have a specified heartbeat_state,
        """
        return self._get_nodes(heartbeat_state)

    @synchronized
    def get_nodes_list(self, heartbeat_state = None):
        return self._get_nodes_list(heartbeat_state)

    @synchronized
    def get_nodes_hash(self, heartbeat_state = None):
        hashlist = []

        for (oan_id, host, port, blocked, heartbeat) in self._get_nodes_list(heartbeat_state):
            hashlist.append( hash( (oan_id, host, port, blocked) ))

        return hash(tuple(hashlist))

    @synchronized
    def send(self, oan_id, message):
        log.debug("oan_id: %s, message: %s" % (oan_id, str(message)))

        if (oan_id in self._nodes):
            node = self._nodes[oan_id]
            if node.is_blocked() and self._my_node.is_blocked():
                self._relay_to_node(oan_id, message)
            else:
                self._send_to_node(node, message)
        else:
            log.info("OANNodeManager:Error node is missing %s" % oan_id)
            log.info(self._nodes)


    @synchronized
    def shutdown(self):
        return True


    '''
    @synchronized
    def send(self, oan_id, message):
        log.debug("oan_id: %s, message: %s" % (oan_id, str(message)))

        if (oan_id in self._nodes):
            node = self._nodes[oan_id]
            if node.is_blocked() and self._my_node.is_blocked():
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



    def dump(self):
        print("------ dump begin ------")
        for n in self._nodes.values():
            print("%s" % n)
        print("------ dump end ------")

    #TODO: not all message should be relay
    #TODO: find good relay nodes. use statistic
    def _relay_to_node(self, destination_uuid, message):
        """
        find a realy node to send a message to a blocked node. this is only
        needed when my node is blocked and the remote node is blocked.
        """

        relay = OANMessageRelay.create(self._my_node.oan_id, destination_uuid, message)
        nodes = self._get_nodes(OANHeartbeat.NOT_OFFLINE)

        # try to find a relay node that already is connected and not blocked
        for relay_node in nodes:
            if not relay_node.is_disconnected() and not relay_node.is_blocked():
                log.info("Relay %s to [%s] through [%s] connected" % (
                    message.__class__.__name__,
                    destination_uuid,
                    relay_node.oan_id))

                self._send_to_node(relay_node, relay)
                return


        # try to find a relay node that is not blocked
        for relay_node in nodes:
            if not relay_node.is_blocked():
                log.info("Relay %s to [%s] through [%s] not connected" % (
                    message.__class__.__name__,
                    destination_uuid,
                    relay_node.oan_id))

                self._send_to_node(relay_node, relay)
                return


        log.warning("Relay %s to [%s] no node found, it will not be sent" % (
            message.__class__.__name__,
            destination_uuid))

        print nodes
        self.dump()

    def _send_to_node(self, node, message):
        """
        sends a message to a node, if the node is not connected
        execute a connect to node command. the message will be
        sent to node when connection is open.

        """

        try:
            log.info("OANNodeManager: send to %s " % node.oan_id)
            node.send(message)
            node.add_message_statistic(message.__class__.__name__, sent_time = True)

            if node.is_disconnected():
                log.info("OANNodeManager: connecting to %s " % node.oan_id)
                network().execute(NetworksCommandConnectToNode.create(node, self._auth))

            if node.out_queue.qsize() == (OANNetworkNode.QUEUE_SIZE * 0.75):
                dispatcher().execute(OANCommandCleanOutQueue.create(node))

        except Full:
            log.warning("Queue is full %s to [%s], will not be sent" % (
                message.__class__.__name__,
                node.oan_id))

    def _create_node(self, oan_id, host, port, blocked):
        """
        create the node in the node dictionary. if the node already exists
        "host,port,blocked" will be updated.

        """

        if oan_id in self._nodes:
            node = self._nodes[oan_id]
            node.update(host = host, port = port,
                        blocked = blocked)
        else:
            node = OANNetworkNode.create(oan_id, host, port, blocked)
            self._nodes[oan_id] = node

        return node


    def _add_node(self, node):
        """
        add a node to the node dictionary. if the node already exists it
        updates the host, port, blocked.
        """
        if node.oan_id in self._nodes:
            n = self._nodes[node.oan_id]
            n.update(host = node.host, port = node.port,
                        blocked = node.blocked)
        else:
            self._nodes[node.oan_id] = node

    def _set_my_node(self, node):
        """
        set my node and update the host, port, blocked from the config.
        """
        if self._my_node is None:
            node.update(
                host = self._config.node_domain_name,
                port = int(self._config.node_port),
                blocked = self._config.blocked)

            self._my_node = node
            self._my_node.touch()
        else:
            log.info("OANNodeManager:Error my node is already set")


    def _create_my_node(self):
        """
        create a new node from config and set it to my node.
        """
        if self._my_node is None:
            node = self._create_node(
                self._config.oan_id,
                self._config.node_domain_name,
                int(self._config.node_port),
                self._config.blocked
            )

            self._my_node = node
            self._my_node.touch()
        else:
            log.info("OANNodeManager:Error my node is already set")


    def _get_nodes(self, heartbeat_state = None, include_my_node = False):
        """
        Returns all nodes that have a specified heartbeat_state,
        """

        ret = []
        for n in self._nodes.values():
            if (
                (include_my_node or n.oan_id != self._my_node.oan_id) and
                (heartbeat_state is None or n.has_heartbeat_state(heartbeat_state))):
                    ret.append(n)

        return ret


    def _get_nodes_list(self, heartbeat_state = None):
        valuelist = []
        for node in self._get_nodes(heartbeat_state, True):
            (
                name,
                host,
                port,
                blocked,
                state,
                heartbeat
            ) = node.get()

            oan_id = str(node.oan_id)
            valuelist.append((oan_id, host, port, blocked, heartbeat))

        valuelist.sort()
        return valuelist
