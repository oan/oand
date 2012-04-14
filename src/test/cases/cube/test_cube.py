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
class Connetions:
    all = {}


class Message:
    origin_url = None


class MessageConnect(Message):
    def execute(self, node):
        for x_pos in xrange(0, len(node.x_list)):
            c_list = node.x_list[x_pos]

            if len(c_list) < 4:
                log.info("1 x: %s y: %s" % (x_pos, node.y_pos) )
                c_list.append(self.origin_url)

                msg = MessageGiveSlotid((x_pos, node.y_pos, 0))
                node.send(self.origin_url, msg)
                return

        if len(node.x_list) == 3:
            if len(node.y_list) <= node.y_pos + 1:
                log.info("2 %s" % len(node.x_list) )
                node.y_list.append([self.origin_url])
                msg = MessageGiveSlotid((0, len(node.y_list)-1, 0))
                node.send(self.origin_url, msg)
            else:
                log.info("3 x:%s y:%s" % (len(node.x_list), len(node.y_list) ))
                msg = MessageConnectOnThisInstead(node.y_list[node.y_pos + 1][0])
                node.send(self.origin_url, msg)

        else:
            log.info("4 %s" % len(node.x_list) )
            node.x_list.append([self.origin_url])
            msg = MessageGiveSlotid((len(node.x_list)-1, node.y_pos, 0))
            node.send(self.origin_url, msg)


class MessageGiveSlotid(Message):
    slot_id = None

    def __init__(self, slot_id):
        self.slot_id = slot_id

    def execute(self, node):
        node.slot_id = self.slot_id
        node.x_pos, node.y_pos, node.z_pos = node.slot_id
        node.send(self.origin_url, MessageSnapshot(self.slot_id, "oan://node-list/all"))


class MessageConnectOnThisInstead(Message):
    bind_url = None
    def __init__(self, bind_url):
        self.bind_url = bind_url
        log.info("connect instead %s" % self.bind_url)

    def execute(self, node):
        node.send(self.bind_url, MessageConnect())


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
                x_list = [[self.origin_url]]

            if x_pos == node.x_pos:
                y_list = node.y_list
            else:
                y_list = [[self.origin_url]]

            z_list = [[]]
            msg = MessageResource((x_list, y_list, z_list))
            node.send(self.origin_url, msg)


class MessageResource():
    resource_list = None

    def __init__(self, resource_list):
        self.resource_list = resource_list

    def execute(self, node):
        x, y, z = self.resource_list
        node.x_list = x[:]
        node.y_list = y[:]
        node.z_list = z[:]


class MessageGetSlotNode(): pass

class MessagePing(): pass
class MessageHeartbeat(): pass
class MessageGetValue(): pass
class MessageSetValue(): pass


class Node():
    bind_url = None
    slot_id = None
    x_list = None
    y_list = None
    z_list = None

    def __init__(self, bind_url):
        self.bind_url = bind_url
        self.slot_id = (0, 0, 0)
        self.x_pos = 0
        self.y_pos = 0
        self.z_pos = 0
        self.x_list = [[bind_url]]
        self.y_list = [[bind_url]]
        self.z_list = [[bind_url]]
        Connetions.all[bind_url] = self

    def send(self, url, message):
        message.origin_url = self.bind_url
        Connetions.all[url].receive(message)

    def push(self, message):
        for node in self.c_list.values():
            self.send(node, message)

    def receive(self, message):
        message.execute(self)


class TestOANCube(OANTestCase):
    database = None

    def setUp(self):
        pass

    def connect_node(self, node_id, slot_id, test_list):
        log.info("Create %s with slot_id %s" % (node_id, slot_id))
        new_node = Node(node_id)
        new_node.send('001', MessageConnect())
        self.assertEqual(new_node.slot_id, slot_id)
        self.assertEqual(new_node.x_list, self.get_x_list(slot_id, test_list))
        #self.assertEqual(new_node.y_list, self.get_y_list(test_list))

    def get_x_list(self, slot_id, test_list):
        x, y, z = slot_id

        new_x_list = []
        for c_list in test_list[y*3:y*3+3]:
            new_c_list = []
            for node in c_list:
                if node != "___":
                    new_c_list.append(str(node))
            if len(new_c_list):
                new_x_list.append(new_c_list)
        log.info('x(%s) %s' % (slot_id, new_x_list))
        return new_x_list

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

        #
        # DEBUG/LOG
        #
        for node in Connetions.all.values():
            log.info("%s %s" % (node.bind_url, node.x_list))

        for node in Connetions.all.values():
            log.info("%s %s" % (node.bind_url, node.slot_id))
