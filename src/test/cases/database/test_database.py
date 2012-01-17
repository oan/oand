#!/usr/bin/env python
'''
Test cases for oan.statistic.py

'''

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from Queue import Queue
from uuid import UUID, uuid4

from test.test_case import OANTestCase
from oan import node_manager
from oan.loop import OANLoop
from oan.event import OANEvent
from oan.application import OANApplication
from oan.config import OANConfig
from oan.node_manager import OANNetworkNode, OANNodeManager
from oan.message import OANMessagePing, OANMessageHeartbeat, OANMessageClose, OANMessageHandshake
from oan.database import OANDatabase

class MyTestNode():
    uuid = None
    host = None
    port = None

    def __init__(self, uuid):
        self.uuid = uuid

    @classmethod
    def create(cls, uuid, host, port):
        obj = cls(uuid)
        obj.host, obj.port = host, port
        return obj

    def unserialize(self, data):
        self.host, self.port = data

    def serialize(self):
        return(self.host, self.port)

    def __str__(self):
        return 'MyTestNode(%s, %s, %s)' % (self.uuid, self.host, self.port)

class TestOANDatabase(OANTestCase):
    database = None

    def setUp(self):
        config = OANConfig(
                '00000000-0000-aaaa-0000-000000000000',
                "TestOANDatabase",
                "localhost",
                str(9000))

        self.database = OANDatabase(config)
        self.database.start()

    def tearDown(self):
        self.database.shutdown()
        self.database = None

    def generate_nodes(self):
        l = []
        for i in xrange(1000):
            l.append(MyTestNode.create(uuid4(), 'localhost', i))

        return l

    def test_select(self):
        n = MyTestNode.create(UUID('31f40446-1565-4b2d-9f61-83e8b4dd5c95'), 'localhost', 4000)
        self.database.replace(n)
        self.assertEqual(self.database.select(MyTestNode, UUID('31f40446-1565-4b2d-9f61-83e8b4dd5c95')).__dict__, n.__dict__)

    def test_insert_all(self):
        l = self.generate_nodes();

        self.database.delete_all(MyTestNode)
        self.database.insert_all(l)

        counter = 0
        for n in self.database.select_all(MyTestNode):
            counter = counter + 1

        self.assertEqual(counter, len(l))



