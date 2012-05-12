#!/usr/bin/env python
"""
Test cases for oan.cube

OAN Cube Rules
* All nodes will push their node lists to their bffs every hour.
  So all nodes can see if any node has expired, and a slot is free.
* When a new node should be assigned a slot, an empty slot is primary taken
  and if none are free an expired slot will be assigned.
* All new slots are choosen from the lowest possible x, y, z coordinate.
* If more then x nodes exist in the same slot, the node with the highest
  node_id (uuid) has to move.

"""

__author__ = "martin@amivono.com, daniel@amivono.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin@amivono.com, daniel@amivono.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"


from test.test_case import OANTestCase
from oan.util import log


class Connections:
    """Roughly emulate a network and time."""

    """
    Holdes a reference to all nodes on the emulated network.
    key   - a bind url ie. "001"
    value - reference to node instance.

    """
    all = {}

    @staticmethod
    def trigger_5minute_cron():
        """
        Emulates a cron job that is executed every 5 minute.

        Naturally a unit test don't have any scheduler/cron, so this function
        should be called manually.

        """
        for node in Connections.all.itervalues():
            node.trigger_5minute_cron()


class Counter:
    """
    Statistics for things done by and to a node.

    receive        - received messages
    push           - pushed messages
    send           - sent messages
    bff_connect    - attempts to reconnect to all bff nodes
    socket_connect - attempts to connect to a socket

    """
    receive = None
    push = None
    send = None
    bff_connect = None
    socket_connect = None

    def __init__(self):
        self.receive = 0
        self.push = 0
        self.send = 0
        self.bff_connect = 0
        self.socket_connect = 0

    def __str__(self):
        return ("receive:{0:>4}, push:{1:>4}, send:{2:>4}, " +
               "bff_connect:{3:>4}, socket_connect:{4:>4}").format(
                    self.receive, self.push, self.send,
                    self.bff_connect, self.socket_connect
                )

    def __iadd__(self, obj):
        if isinstance(obj, Counter):
            self.receive += obj.receive
            self.push += obj.push
            self.send += obj.send
            self.bff_connect += obj.bff_connect
            self.socket_connect += obj.socket_connect
            return self
        else:
            raise TypeError("Not a Counter object.")


class SlotId:
    """
    The position of a slot in the cube.

    """
    x = None
    y = None
    z = None

    def __init__(self, x = 0 , y = 0 , z = 0):
        self.x = x
        self.y = y
        self.z = z

    def id(self):
        return (self.x, self.y ,self.z)

class NodeList:
    """
    List of nodes in x, y, z direction.

    """
    s = None
    x = None
    y = None
    z = None

    def __init__(self):
        self.s = []
        self.x = [self.s]
        self.y = [self.s]
        self.z = [self.s]


class Node():
    """
    A computer node.

    """

    # Bind address to this node.
    bind_url = None

    # Coordinates/slot_id of the slot assigned to this node.
    slot = None

    # Lists of nodes in x, y, z direction.
    node_list = None

    # Emulation of sockets/nodes this node is connected to.
    sockets = None

    # Statistic counters.
    counter = None

    def __init__(self, bind_url):
        self.bind_url = bind_url
        self.slot = SlotId()
        self.node_list = NodeList()
        self.node_list.s.append(bind_url)

        self.sockets = {'c': [], 'x': [], 'y': [], 'z': []}
        self.counter = Counter()

        # Start listening for connections.
        Connections.all[bind_url] = self

    def trigger_5minute_cron(self):
        """
        Called every 5 minute.

        Reconnect if nodes has been disconnected, or new node are online.

        """
        self.connect_to_bff_nodes()

    def connect_to_bff_nodes(self):
        """
        Connect to all bff nodes in s, x, y, z direction.

        * Each node will communicate with all other nodes in the same slot.
        * Each node will communicate with one node in the the nearest slot forward
          and backward in x, y and z direction.
        * Each node will communicate with one node in a slot that is faraway forward
          and backward in x, y and z direction. Faraway is rougly defined as
          x_pos + (max_x_size/2).

        """
        self.counter.bff_connect += 1
        old_sockets = { key : set(value) for key, value in self.sockets.items()}
        self.sockets = {'c': [], 'x': [], 'y': [], 'z': []}
        self._connect_to_all_in_current_slot("c")

        #self._connect_to_previous_slot(self.slot.x, self.node_list.x, "x")
        self._connect_to_next_slot(self.slot.x, self.node_list.x, "x")
        #self._connect_to_faraway_previous_slot(self.slot.x, self.node_list.x, "x")
        self._connect_to_faraway_slot(self.slot.x, self.node_list.x, "x")

        #self._connect_to_previous_slot(self.slot.y, self.node_list.y, "y")
        self._connect_to_next_slot(self.slot.y, self.node_list.y, "y")
        #self._connect_to_faraway_previous_slot(self.slot.y, self.node_list.y, "y")
        self._connect_to_faraway_slot(self.slot.y, self.node_list.y, "y")

        new_sockets = { key:set(value) for key, value in self.sockets.items()}
        new_connections =  {key:new_sockets[key] - old_sockets[key] for key, value in new_sockets.items()}
        if new_connections:
            log.info(self.bind_url + " Connect to bff nodes %s" % new_connections)
            log.info(self.bind_url + " is now connected to %s" % self.sockets)

    def _connect_to_all_in_current_slot(self, direction):
        """Connect to all nodes in current slot."""
        for bind_url in self.node_list.x[self.slot.x]:
            self._connect_socket(bind_url, direction)

    def _connect_to_next_slot(self, pos, local_list, direction):
        """Connect to the next slot, the slot after current slot."""
        if pos >= len(local_list)-1:
            # If current slot is the last slot, connect to first slot,
            if pos != 0:
                if len(local_list[0]) > 0:
                    self._connect_socket(local_list[0][0], direction)
        elif pos + 1 <= len(local_list)-1:
            # Connect to next node if it exists.
            self._connect_socket(local_list[pos + 1][0], direction)

    def _connect_to_faraway_slot(self, pos, local_list, direction):
        """Connect to a faraway slot."""
        # TODO
        return
        local_list_middle = (len(local_list)/2)
        q_far = pos + local_list_middle

        if q_far >= len(local_list):
            q_far -= len(local_list)

        if q_far in local_list:
            self._connect_socket(local_list[q_far][0], direction)

    def _connect_socket(self, bind_url, direction):
        if bind_url != self.bind_url and not self._is_already_connected(bind_url):
            self.counter.socket_connect += 1
            log.info(self.bind_url + " Connect to socket: %s to %s on %s-list" % (self.bind_url, bind_url, direction))
            self.sockets[direction].append(bind_url)

            #if self.bind_url not in Connections.all[bind_url].sockets[direction]:
            #    Connections.all[bind_url].sockets[direction].append(self.bind_url)

    def _is_already_connected(self, bind_url):
        for direction in self.sockets:
            if bind_url in self.sockets[direction]:
                return True
        return False


    def send(self, url, message):
        self.counter.send += 1
        log.info("Send: %s from %s to %s " % (message.__class__.__name__, self.bind_url, Connections.all[url].bind_url))
        message.origin_url = self.bind_url
        Connections.all[url].receive(message)

    def push(self, direction, message):
        self.counter.push += 1
        for bind_url in self.sockets[direction]:
            self.send(bind_url, message)

    def receive(self, message):
        self.counter.receive += 1
        message.execute(self)




class Message(object):
    """Base class for all Messages."""

    """
    The bind url for the node that sends the message.

    """
    origin_url = None


class MessageConnect(Message):
    def execute(self, node):
        c_max_list = 4
        if len(node.node_list.y[len(node.node_list.y)-1]) < c_max_list:
            x_max_size = max(3, len(node.node_list.y)-1)
        else:
            x_max_size = max(3, len(node.node_list.y))
        log.info("X-max-size: %s, x: %s, y: %s" % (
                 x_max_size, len(node.node_list.x), len(node.node_list.y)))

        for x_pos in xrange(0, len(node.node_list.x)):
            c_list = node.node_list.x[x_pos]

            if len(c_list) < c_max_list:
                log.info("Step: 1 x: %s y: %s" % (x_pos, node.slot.y) )
                c_list.append(self.origin_url)

                msg = MessageGiveSlotid(SlotId(x_pos, node.slot.y, 0))
                node.send(self.origin_url, msg)
                node.push('c', MessageGiveNodeList('x', node.node_list.x))
                node.push('c', MessageGiveNodeList('y', node.node_list.y))
                node.push('c', MessageGiveNodeList('z', node.node_list.z))
                return

        if len(node.node_list.x) == x_max_size:
            if len(node.node_list.y) <= node.slot.y + 1:
                log.info("Step: 2 %s" % len(node.node_list.x) )
                node.node_list.y.append([self.origin_url])
                msg = MessageGiveSlotid(SlotId(0, len(node.node_list.y)-1, 0))
                node.send(self.origin_url, msg)
                node.push('y', MessageGiveNodeList('y', node.node_list.y))
                node.push('c', MessageGiveNodeList('y', node.node_list.y))
            else:
                log.info("Step: 3 x:%s y:%s" % (len(node.node_list.x), len(node.node_list.y) ))
                msg = MessageRedirect(node.node_list.y[node.slot.y + 1][0], self)
                node.send(self.origin_url, msg)
        else:
            log.info("Step: 4 %s" % len(node.node_list.x) )
            node.node_list.x.append([self.origin_url])
            msg = MessageGiveSlotid(SlotId(len(node.node_list.x)-1, node.slot.y, 0))
            node.send(self.origin_url, msg)
            node.push('x', MessageGiveNodeList('x', node.node_list.x))
            node.push('c', MessageGiveNodeList('x', node.node_list.x))


class MessageGiveSlotid(Message):
    slot = None

    def __init__(self, slot):
        self.slot = slot

    def execute(self, node):
        node.slot = self.slot
        node.send(self.origin_url, MessageSnapshot(self.slot, "oan://node-list/all"))


class MessageRedirect(Message):
    bind_url = None
    message = None
    def __init__(self, bind_url, message):
        self.bind_url = bind_url
        self.message = message
        log.info("Redirect %s to %s" % (
                 self.message.__class__.__name__, self.bind_url))

    def execute(self, node):
        node.send(self.bind_url, self.message)


class MessageSnapshot(Message):
    origin_slot = None
    url = None

    def __init__(self, slot, url):
        self.origin_slot = slot
        self.url = url

    def execute(self, node):
        if self.url == "oan://node-list/all":
            x_pos, y_pos, z_pos = self.origin_slot.id()
            if y_pos == node.slot.y:
                x_list = node.node_list.x
            else:
                x_list = []
                for pos in xrange(0, x_pos):
                    x_list.append([])
                x_list.append(node.node_list.y[y_pos])

            if x_pos == node.slot.x:
                y_list = node.node_list.y
            else:
                y_list = []
                for pos in xrange(0, y_pos):
                    y_list.append([])
                y_list.append(node.node_list.x[x_pos])

            z_list = [[]]

            msg = MessageGiveSnapshotResource(x_list, y_list, z_list)
            node.send(self.origin_url, msg)


class MessageGiveSnapshotResource(Message):
    node_list= None

    def __init__(self, x, y, z):
        self.node_list = NodeList()
        self.node_list.x = x[:]
        self.node_list.y = y[:]
        self.node_list.z = z[:]

    def execute(self, node):
        node.node_list.x = self.node_list.x
        node.node_list.y = self.node_list.y
        node.node_list.z = self.node_list.z

        #todo self.sync_x_list(node)
        self.sync_y_list(node)

        node.connect_to_bff_nodes()

        node.push('x', MessageGiveNodeList('x', node.node_list.x))
        node.push('y', MessageGiveNodeList('y', node.node_list.y))
        node.push('z', MessageGiveNodeList('z', node.node_list.z))

        node.push('c', MessageGiveNodeList('x', node.node_list.x))
        node.push('c', MessageGiveNodeList('y', node.node_list.y))
        node.push('c', MessageGiveNodeList('z', node.node_list.z))

    def empty_list(self, node, local_list):
        """Check if only one slot is occupied in y-list"""
        for c_list in local_list:
            if len(c_list) > 0 and node.bind_url not in c_list:
                return False
        return True

    def sync_y_list(self, node):
        if self.empty_list(node, node.node_list.y) and node.slot.y != 0:
            log.info("sync_y_list")

            left_origin_url = node.node_list.x[node.slot.x - 1][0]
            msg = MessageGetYList(node.slot.x, node.slot.y)
            node.send(left_origin_url, msg)


class MessageGetYList(Message):
    slot = None

    def __init__(self, x_pos, y_pos):
        self.slot = SlotId()
        self.slot.x = x_pos
        self.slot.y = y_pos

    def execute(self, node):
        log.info("MessageGetYList slot:%s x:%s y:%s x_pos %s of %s" % (
                 node.bind_url,
                 node.slot.x, node.slot.y,
                 self.slot.x, len(node.node_list.x)))
        log.info(node.node_list.x)
        if self.slot.x == node.slot.x and self.slot.y > node.slot.y:
            log.info("MessageGetYList step 1 to %s" % self.origin_url)
            node.send(self.origin_url, MessageGiveNodeList('y', node.node_list.y))
        elif (len(node.node_list.x)-1 >= self.slot.x and
              len(node.node_list.x[self.slot.x]) > 0 and
              self.slot.y > node.slot.y):
            log.info("MessageGetYList step 2 to %s" % node.node_list.x[self.slot.x][0])
            msg = MessageRedirect(node.node_list.x[self.slot.x][0], self)
            node.send(self.origin_url, msg)
        elif self.slot.y >= node.slot.y:
            destination_url = None
            for y in reversed(xrange(node.slot.y)):
                log.info("y %s" % y)
                if len(node.node_list.y[y]) > 0:
                    destination_url = node.node_list.y[y][0]
                    log.info("hit 1")
                    break

            if not destination_url:
                for x in reversed(xrange(node.slot.x)):
                    log.info("x %s" % x)
                    if len(node.node_list.x[x]) > 0:
                        destination_url = node.node_list.x[x][0]
                        log.info("hit 2")
                        break
            log.info("MessageGetYList step 3 to %s" % destination_url)
            if destination_url:
                msg = MessageRedirect(destination_url, self)
                node.send(self.origin_url, msg)


class MessageGiveNodeList(Message):
    direction = None
    remote_list = None

    def __init__(self, direction, remote_list):
        self.direction = direction
        self.remote_list = remote_list[:]

    def execute(self, node):
        log.info("On %s Merge list %s" % (node.bind_url, self.direction))
        if self.direction == 'x':
            changed = self.merge_node_list(node.node_list.x, self.remote_list)
        elif self.direction == 'y':
            changed = self.merge_node_list(node.node_list.y, self.remote_list)
        elif self.direction == 'z':
            changed = self.merge_node_list(node.node_list.z, self.remote_list)

        # Forward new synced list to all bff nodes.
        if changed:
            log.info("Forward sync")
            msg = MessageGiveNodeList(self.direction, self.remote_list)
            node.push(self.direction, msg)

    def merge_node_list(self, local_list, remote_list):
        changed = False
        pos = 0
        log.info("local_list %s" % local_list)

        for slot in remote_list:
            for node_bind_url in slot:
                if pos > len(local_list)-1:
                    local_list.append([node_bind_url])
                    changed = True
                elif not node_bind_url in local_list[pos]:
                    local_list[pos].append(node_bind_url)
                    changed = True

            pos +=1
        log.info("after %s" % local_list)
        return changed


class MessageGetSlotNode(): pass
class MessagePing(): pass
class MessageHeartbeat(): pass
class MessageGetValue(): pass
class MessageSetValue(): pass





class TestOANCube(OANTestCase):
    database = None

    def setUp(self):
        pass

    def connect_node(self, node_id, slot_id, test_list):
        log.info("======= %s =======================================================================================" % node_id)
        log.info("Create %s with slot_id %s" % (node_id, slot_id))
        node = Node(node_id)
        node.send('001', MessageConnect())
        Connections.trigger_5minute_cron()

        x_max_size = max(3, len(Connections.all['001'].node_list.x))

        self.assertEqual(node.slot.id(), slot_id)

        x_list = self.get_x_list(slot_id, test_list, x_max_size)
        self.assertEqual(node.node_list.x, x_list)

        y_list = self.get_y_list(slot_id, test_list, x_max_size)
        self.assertEqual(node.node_list.y, y_list)

    def get_x_list(self, slot_id, test_list, width):
        x, y, z = slot_id

        new_x_list = []
        for c_list in test_list[y*width:y*width+width]:
            new_c_list = []
            for node in c_list:
                if node != "___":
                    new_c_list.append(str(node))
            if len(new_c_list):
                new_x_list.append(new_c_list)
        log.info('Expected: x(%s) %s' % (slot_id, new_x_list))
        return new_x_list

    def get_y_list(self, slot_id, test_list, width):
        x, y, z = slot_id

        new_y_list = []
        for slot_pos in xrange(x, len(test_list), width):
            c_list = test_list[slot_pos]
            log.info("slot_id %s slot_pos %s %s" % (slot_id, slot_pos, c_list))
            new_c_list = []
            for node in c_list:
                if node != "___":
                    new_c_list.append(str(node))
            if len(new_c_list):
                new_y_list.append(new_c_list)
        log.info('Expected: y(%s) %s' % (slot_id, new_y_list))
        return new_y_list

    def test_connection(self):
        first_node = Node('001')
        self.assertEqual(first_node.slot.id(), (0, 0, 0))

        self.connect_node("002", (0, 0, 0), [["001", "002", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("003", (0, 0, 0), [["001", "002", "003", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("004", (0, 0, 0), [["001", "002", "003", "004"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("005", (1, 0, 0), [["001", "002", "003", "004"], ["005", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("006", (1, 0, 0), [["001", "002", "003", "004"], ["005", "006", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("007", (1, 0, 0), [["001", "002", "003", "004"], ["005", "006", "007", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("008", (1, 0, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("009", (2, 0, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("010", (2, 0, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("011", (2, 0, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("012", (2, 0, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("013", (0, 1, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("014", (0, 1, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("015", (0, 1, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("016", (0, 1, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["___", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("017", (1, 1, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "___", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("018", (1, 1, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "___", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("019", (1, 1, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "___"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("020", (1, 1, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["___", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("021", (2, 1, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "___", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("022", (2, 1, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "___", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("023", (2, 1, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "___"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("024", (2, 1, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"],
                                             ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("025", (0, 2, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"],
                                             ["025", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("026", (0, 2, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"],
                                             ["025", "026", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("027", (0, 2, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"],
                                             ["025", "026", "027", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("028", (0, 2, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"],
                                             ["025", "026", "027", "028"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("029", (1, 2, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"],
                                             ["025", "026", "027", "028"], ["029", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("030", (1, 2, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"],
                                             ["025", "026", "027", "028"], ["029", "030", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("031", (1, 2, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "___"], ["___", "___", "___", "___"]])

        self.connect_node("032", (1, 2, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["___", "___", "___", "___"]])

        self.connect_node("033", (2, 2, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "___", "___", "___"]])

        self.connect_node("034", (2, 2, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "___", "___"]])

        self.connect_node("035", (2, 2, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "___"]])

        self.connect_node("036", (2, 2, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"]])

        self.connect_node("037", (0, 3, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"],
                                             ["037", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("038", (0, 3, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"],
                                             ["037", "038", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("039", (0, 3, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"],
                                             ["037", "038", "039", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("040", (0, 3, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"],
                                             ["037", "038", "039", "040"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])


        self.connect_node("041", (3, 0, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "___", "___", "___"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["___", "___", "___", "___"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["___", "___", "___", "___"],
                                             ["037", "038", "039", "040"], ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("042", (3, 0, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "___", "___"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["___", "___", "___", "___"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["___", "___", "___", "___"],
                                             ["037", "038", "039", "040"], ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("043", (3, 0, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "___"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["___", "___", "___", "___"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["___", "___", "___", "___"],
                                             ["037", "038", "039", "040"], ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("044", (3, 0, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["___", "___", "___", "___"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["___", "___", "___", "___"],
                                             ["037", "038", "039", "040"], ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("045", (3, 1, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "___", "___", "___"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["___", "___", "___", "___"],
                                             ["037", "038", "039", "040"], ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("046", (3, 1, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "___", "___"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["___", "___", "___", "___"],
                                             ["037", "038", "039", "040"], ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("047", (3, 1, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "___"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["___", "___", "___", "___"],
                                             ["037", "038", "039", "040"], ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("048", (3, 1, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "048"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["___", "___", "___", "___"],
                                             ["037", "038", "039", "040"], ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("049", (3, 2, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "048"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["049", "___", "___", "___"],
                                             ["037", "038", "039", "040"], ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("050", (3, 2, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "048"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["049", "050", "___", "___"],
                                             ["037", "038", "039", "040"], ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("051", (3, 2, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "048"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["049", "050", "051", "___"],
                                             ["037", "038", "039", "040"], ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("052", (3, 2, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "048"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["049", "050", "051", "052"],
                                             ["037", "038", "039", "040"], ["___", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("053", (1, 3, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "048"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["049", "050", "051", "052"],
                                             ["037", "038", "039", "040"], ["053", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("054", (1, 3, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "048"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["049", "050", "051", "052"],
                                             ["037", "038", "039", "040"], ["053", "054", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("055", (1, 3, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "048"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["049", "050", "051", "052"],
                                             ["037", "038", "039", "040"], ["053", "054", "055", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("056", (1, 3, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "048"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["049", "050", "051", "052"],
                                             ["037", "038", "039", "040"], ["053", "054", "055", "056"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("057", (2, 3, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "048"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["049", "050", "051", "052"],
                                             ["037", "038", "039", "040"], ["053", "054", "055", "056"], ["057", "___", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("058", (2, 3, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "048"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["049", "050", "051", "052"],
                                             ["037", "038", "039", "040"], ["053", "054", "055", "056"], ["057", "058", "___", "___"], ["___", "___", "___", "___"]])

        self.connect_node("059", (2, 3, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "048"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["049", "050", "051", "052"],
                                             ["037", "038", "039", "040"], ["053", "054", "055", "056"], ["057", "058", "059", "___"], ["___", "___", "___", "___"]])

        self.connect_node("060", (2, 3, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "048"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["049", "050", "051", "052"],
                                             ["037", "038", "039", "040"], ["053", "054", "055", "056"], ["057", "058", "059", "060"], ["___", "___", "___", "___"]])

        self.connect_node("061", (3, 3, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "048"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["049", "050", "051", "052"],
                                             ["037", "038", "039", "040"], ["053", "054", "055", "056"], ["057", "058", "059", "060"], ["061", "___", "___", "___"]])

        self.connect_node("062", (3, 3, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "048"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["049", "050", "051", "052"],
                                             ["037", "038", "039", "040"], ["053", "054", "055", "056"], ["057", "058", "059", "060"], ["061", "062", "___", "___"]])

        self.connect_node("063", (3, 3, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "048"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["049", "050", "051", "052"],
                                             ["037", "038", "039", "040"], ["053", "054", "055", "056"], ["057", "058", "059", "060"], ["061", "062", "063", "___"]])

        self.connect_node("064", (3, 3, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
                                             ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "048"],
                                             ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["049", "050", "051", "052"],
                                             ["037", "038", "039", "040"], ["053", "054", "055", "056"], ["057", "058", "059", "060"], ["061", "062", "063", "064"]])

        #
        # DEBUG/LO
        #
        keys = Connections.all.keys()
        keys.sort()

        log.info("=========================")
        for node_key in keys:
            node = Connections.all[node_key]
            log.info("x-list: %s %s" % (node.bind_url, node.node_list.x))

        log.info("=========================")
        for node_key in keys:
            node = Connections.all[node_key]
            log.info("slot_id: %s %s" % (node.bind_url, node.slot.id()))

        log.info("=========================")
        for node_key in keys:
            node = Connections.all[node_key]
            log.info("Sockets: %s %s" % (node.bind_url, node.sockets))

        log.info("=========================")
        counter_total = Counter()
        for node_key in keys:
            node = Connections.all[node_key]
            log.info("Counters: %s %s" % (node.bind_url, node.counter))
            counter_total += node.counter
        log.info("TOTAL         %s" % (counter_total))

