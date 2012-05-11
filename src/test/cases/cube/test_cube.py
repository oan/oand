#!/usr/bin/env python
'''
Test cases for oan.cube

'''

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from test.test_case import OANTestCase
from oan.util import log


'''
# * Alla noder skickar sin node lista till sina 3 kompisar varje timme.
#   Pa det sattet sa far du reda pa om nagon node ar dad, och en slot har blivit
#   ledig.
# * Nar en ny slot ska tilldelas sa tas i farsta hand en slot som ar helt tom,
#   och i andra hand en slot som ar "dad" och i tredje hand pa annan niva.
# * Alla nya slottar valjs ifran lagsta x,y,z kordinat.
# * Alla nya slottar valjs ifran den y,z list som har lagst antal nodes.
# * Om tva noder har samma slot, far den som har lagst uuid behalla slotten.
# * Valj ut tre noder per x/y/z list att kommunicera med.
'''
class Connections:
    all = {}

    @staticmethod
    def trigger_5minute_cron():
        for node in Connections.all.itervalues():
            node.trigger_5minute_cron()


class Message:
    origin_url = None
    destination_slot_id = None


class MessageConnect(Message):
    def execute(self, node):
        #@todo: What is added to current pos in x_list should also be added to current pos y_list.

        c_max_list = 4
        if len(node.y_list[len(node.y_list)-1]) < c_max_list:
            x_max_size = max(3, len(node.y_list)-1)
        else:
            x_max_size = max(3, len(node.y_list))
        log.info("X-max-size: %s, x: %s, y: %s" % (
                 x_max_size, len(node.x_list), len(node.y_list)))

        for x_pos in xrange(0, len(node.x_list)):
            c_list = node.x_list[x_pos]

            if len(c_list) < c_max_list:
                log.info("Step: 1 x: %s y: %s" % (x_pos, node.y_pos) )
                c_list.append(self.origin_url)

                msg = MessageGiveSlotid((x_pos, node.y_pos, 0))
                node.send(self.origin_url, msg)
                node.push('c', MessageGiveNodeList('x', node.x_list))
                node.push('c', MessageGiveNodeList('y', node.y_list))
                node.push('c', MessageGiveNodeList('z', node.z_list))
                return

        if len(node.x_list) == x_max_size:
            if len(node.y_list) <= node.y_pos + 1:
                log.info("Step: 2 %s" % len(node.x_list) )
                node.y_list.append([self.origin_url])
                msg = MessageGiveSlotid((0, len(node.y_list)-1, 0))
                node.send(self.origin_url, msg)
                node.push('y', MessageGiveNodeList('y', node.y_list))
                node.push('c', MessageGiveNodeList('y', node.y_list))
            else:
                log.info("Step: 3 x:%s y:%s" % (len(node.x_list), len(node.y_list) ))
                msg = MessageRedirect(node.y_list[node.y_pos + 1][0], self)
                node.send(self.origin_url, msg)
        else:
            log.info("Step: 4 %s" % len(node.x_list) )
            node.x_list.append([self.origin_url])
            msg = MessageGiveSlotid((len(node.x_list)-1, node.y_pos, 0))
            node.send(self.origin_url, msg)
            node.push('x', MessageGiveNodeList('x', node.x_list))
            node.push('c', MessageGiveNodeList('x', node.x_list))


class MessageGiveSlotid(Message):
    slot_id = None

    def __init__(self, slot_id):
        self.slot_id = slot_id

    def execute(self, node):
        node.slot_id = self.slot_id
        node.x_pos, node.y_pos, node.z_pos = node.slot_id
        node.send(self.origin_url, MessageSnapshot(self.slot_id, "oan://node-list/all"))


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
    origin_slot_id = None
    url = None

    def __init__(self, slot_id, url):
        self.origin_slot_id = slot_id
        self.url = url

    def execute(self, node):
        if self.url == "oan://node-list/all":
            x_pos, y_pos, z_pos = self.origin_slot_id
            if y_pos == node.y_pos:
                x_list = node.x_list
            else:
                x_list = []
                for pos in xrange(0, x_pos):
                    x_list.append([])
                x_list.append(node.y_list[y_pos])

            if x_pos == node.x_pos:
                y_list = node.y_list
            else:
                y_list = []
                for pos in xrange(0, y_pos):
                    y_list.append([])
                y_list.append(node.x_list[x_pos])

            z_list = [[]]

            msg = MessageGiveSnapshotResource(x_list, y_list, z_list)
            node.send(self.origin_url, msg)


class MessageGiveSnapshotResource(Message):
    x_list = None
    y_list = None
    z_list = None

    def __init__(self, x, y, z):
        self.x_list = x[:]
        self.y_list = y[:]
        self.z_list = z[:]

    def execute(self, node):
        node.x_list = self.x_list
        node.y_list = self.y_list
        node.z_list = self.z_list

        #todo self.sync_x_list(node)
        self.sync_y_list(node)

        node.connect_to_bff_nodes()

        node.push('x', MessageGiveNodeList('x', node.x_list))
        node.push('y', MessageGiveNodeList('y', node.y_list))
        node.push('z', MessageGiveNodeList('z', node.z_list))

        node.push('c', MessageGiveNodeList('x', node.x_list))
        node.push('c', MessageGiveNodeList('y', node.y_list))
        node.push('c', MessageGiveNodeList('z', node.z_list))

    def empty_list(self, node, local_list):
        """Check if only one slot is occupied in y-list"""
        for c_list in local_list:
            if len(c_list) > 0 and node.bind_url not in c_list:
                return False
        return True

    def sync_y_list(self, node):
        if self.empty_list(node, node.y_list) and node.y_pos != 0:
            log.info("sync_y_list")

            left_origin_url = node.x_list[node.x_pos - 1][0]
            msg = MessageGetYList(node.x_pos, node.y_pos)
            node.send(left_origin_url, msg)


class MessageGetYList(Message):
    x_pos = None
    y_pos = None

    def __init__(self, x_pos, y_pos):
        self.x_pos = x_pos
        self.y_pos = y_pos

    def execute(self, node):
        log.info("MessageGetYList slot:%s x:%s y:%s x_pos %s of %s" % (
                 node.bind_url,
                 node.x_pos, node.y_pos,
                 self.x_pos, len(node.x_list)))
        log.info(node.x_list)
        if self.x_pos == node.x_pos and self.y_pos > node.y_pos:
            log.info("MessageGetYList step 1 to %s" % self.origin_url)
            node.send(self.origin_url, MessageGiveNodeList('y', node.y_list))
        elif (len(node.x_list)-1 >= self.x_pos and
              len(node.x_list[self.x_pos]) > 0 and
              self.y_pos > node.y_pos):
            log.info("MessageGetYList step 2 to %s" % node.x_list[self.x_pos][0])
            msg = MessageRedirect(node.x_list[self.x_pos][0], self)
            node.send(self.origin_url, msg)
        elif self.y_pos >= node.y_pos:
            destination_url = None
            for y in reversed(xrange(node.y_pos)):
                log.info("y %s" % y)
                if len(node.y_list[y]) > 0:
                    destination_url = node.y_list[y][0]
                    log.info("hit 1")
                    break

            if not destination_url:
                for x in reversed(xrange(node.x_pos)):
                    log.info("x %s" % x)
                    if len(node.x_list[x]) > 0:
                        destination_url = node.x_list[x][0]
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
            changed = self.merge_node_list(node.x_list, self.remote_list)
        elif self.direction == 'y':
            changed = self.merge_node_list(node.y_list, self.remote_list)
        elif self.direction == 'z':
            changed = self.merge_node_list(node.z_list, self.remote_list)

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


class Counter:
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
                    self.receive,
                    self.push,
                    self.send,
                    self.bff_connect,
                    self.socket_connect
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


class Node():
    bind_url = None
    slot_id = None
    c_list = None
    x_list = None
    y_list = None
    z_list = None
    x_pos = None
    y_pos = None
    z_pos = None
    sockets = None
    counter = None

    def __init__(self, bind_url):
        self.bind_url = bind_url
        self.slot_id = (0, 0, 0)
        self.x_pos = 0
        self.y_pos = 0
        self.z_pos = 0
        self.c_list = [bind_url]
        self.x_list = [self.c_list]
        self.y_list = [self.c_list]
        self.z_list = [self.c_list]
        self.sockets = {'c': [], 'x': [], 'y': [], 'z': []}
        self.counter = Counter()

        Connections.all[bind_url] = self

    def trigger_5minute_cron(self):
        # Reconnect if nodes has been disconnected, or new node are oline.
        self.connect_to_bff_nodes()

    def connect_to_bff_nodes(self):
        self.counter.bff_connect += 1
        old_sockets = { key : set(value) for key, value in self.sockets.items()}
        self.sockets = {'c': [], 'x': [], 'y': [], 'z': []}
        self._connect_to_all_in_current_slot("c")

        self._connect_to_next_slot(self.x_pos, self.x_list, "x")
        # TODO
        #self._connect_to_faraway_slot(self.x_pos, self.x_list, "x")

        self._connect_to_next_slot(self.y_pos, self.y_list, "y")
        # TODO
        #self._connect_to_faraway_slot(self.y_pos, self.y_list, "y")

        new_sockets = { key:set(value) for key, value in self.sockets.items()}
        new_connections =  {key:new_sockets[key] - old_sockets[key] for key, value in new_sockets.items()}
        if new_connections:
            log.info(self.bind_url + " Connect to bff nodes %s" % new_connections)
            log.info(self.bind_url + " is now connected to %s" % self.sockets)

    def _connect_to_all_in_current_slot(self, direction):
        """Connect to all nodes in current slot."""
        for bind_url in self.x_list[self.x_pos]:
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
        local_list_middle = (len(local_list)/2)
        q_far = pos + local_list_middle

        if q_far >= len(local_list):
            q_far -= len(local_list)

        if q_far in local_list:
            self._connect_socket(local_list[q_far][0], direction)

    def _connect_socket(self, bind_url, direction):
        if bind_url != self.bind_url and bind_url not in self.sockets[direction]:
            self.counter.socket_connect += 1
            log.info(self.bind_url + " Connect to socket: %s to %s on %s-list" % (self.bind_url, bind_url, direction))
            self.sockets[direction].append(bind_url)

            #if self.bind_url not in Connections.all[bind_url].sockets[direction]:
            #    Connections.all[bind_url].sockets[direction].append(self.bind_url)

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
        if (message.destination_slot_id == None or
            message.destination_slot_id == self.slot_id):
            message.execute(self)
        else:
            dst_x, dst_y, dst_z = message.destination_slot_id
            if dst_x == self.x_pos:
                self.send(self.y_list[dst_y][0], message)
            elif dst_y == self.y_pos:
                self.send(self.x_list[dst_x][0], message)


class TestOANCube(OANTestCase):
    database = None

    def setUp(self):
        pass

    def connect_node(self, node_id, slot_id, test_list):
        log.info("======= %s =======================================================================================" % node_id)
        log.info("Create %s with slot_id %s" % (node_id, slot_id))
        new_node = Node(node_id)
        new_node.send('001', MessageConnect())
        Connections.trigger_5minute_cron()

        x_max_size = max(3, len(new_node.x_list))

        self.assertEqual(new_node.slot_id, slot_id)

        x_list = self.get_x_list(slot_id, test_list, x_max_size)
        self.assertEqual(new_node.x_list, x_list)

        y_list = self.get_y_list(slot_id, test_list, x_max_size)
        self.assertEqual(new_node.y_list, y_list)

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
        self.assertEqual(first_node.slot_id, (0, 0, 0))

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


        # self.connect_node("053", (1, 3, 0), [["001", "002", "003", "004"], ["005", "006", "007", "008"], ["009", "010", "011", "012"], ["041", "042", "043", "044"],
        #                                      ["013", "014", "015", "016"], ["017", "018", "019", "020"], ["021", "022", "023", "024"], ["045", "046", "047", "048"],
        #                                      ["025", "026", "027", "028"], ["029", "030", "031", "032"], ["033", "034", "035", "036"], ["049", "050", "051", "052"],
        #                                      ["037", "038", "039", "040"], ["053", "___", "___", "___"], ["___", "___", "___", "___"], ["___", "___", "___", "___"]])



        #
        # DEBUG/LO
        #
        keys = Connections.all.keys()
        keys.sort()

        log.info("=========================")
        for node_key in keys:
            node = Connections.all[node_key]
            log.info("x-list: %s %s" % (node.bind_url, node.x_list))

        log.info("=========================")
        for node_key in keys:
            node = Connections.all[node_key]
            log.info("slot_id: %s %s" % (node.bind_url, node.slot_id))

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

