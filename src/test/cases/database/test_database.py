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
        self.database.delete_all(MyTestNode)

    def tearDown(self):
        self.database.shutdown()
        self.database = None

    def generate_nodes(self):
        l = []
        for i in xrange(1000):
            l.append(MyTestNode.create(uuid4(), 'localhost', i))

        return l


    def test_count(self):
        # Test that table is empty
        self.assertEqual(self.database.count(MyTestNode), 0)

        # Insert one row
        n = MyTestNode.create(UUID('31f40446-1565-4b2d-9f61-83e8b4dd5c95'), 'localhost', 4000)
        self.database.insert(n)

        # Test that table have one row
        self.assertEqual(self.database.count(MyTestNode), 1)




    def test_delete(self):
        # Insert rows
        rows = self.generate_nodes()
        self.database.insert_all(rows)

        # Test that table have all rows
        self.assertEqual(self.database.count(MyTestNode), len(rows))

        n = MyTestNode.create(UUID('31f40446-1565-4b2d-9f61-83e8b4dd5c95'), 'localhost', 4000)
        self.database.insert(n)

        # Test that table have the last insert rows
        self.assertEqual(self.database.count(MyTestNode), len(rows)+1)

        # retrieve the row and check that it's has the same attribute
        self.assertEqual(self.database.select(MyTestNode, UUID('31f40446-1565-4b2d-9f61-83e8b4dd5c95')).__dict__, n.__dict__)

        # Delete the row
        self.database.delete(MyTestNode, UUID('31f40446-1565-4b2d-9f61-83e8b4dd5c95'))

        # Test that one row is missing
        self.assertEqual(self.database.count(MyTestNode), len(rows))

        # try to retrieve the row is should return None
        self.assertEqual(self.database.select(MyTestNode, UUID('31f40446-1565-4b2d-9f61-83e8b4dd5c95')), None)




    def test_delete_all(self):
        # Insert rows
        rows = self.generate_nodes()
        self.database.insert_all(rows)

        # Test that table have all rows
        self.assertEqual(self.database.count(MyTestNode), len(rows))

        # Delete them
        self.database.delete_all(MyTestNode)

        # Table should be empty
        self.assertEqual(self.database.count(MyTestNode), 0)





    def test_select(self):
        # insert a row
        n = MyTestNode.create(UUID('31f40446-1565-4b2d-9f61-83e8b4dd5c95'), 'localhost', 4000)
        self.database.insert(n)

        # retrieve the row and check that it's has the same attribute
        self.assertEqual(self.database.select(MyTestNode, UUID('31f40446-1565-4b2d-9f61-83e8b4dd5c95')).__dict__, n.__dict__)



    def test_select_all(self):
        # Insert rows
        rows = self.generate_nodes()
        self.database.insert_all(rows)

        # retrieve the rows and check that it's has the same attribute
        i = 0
        for db_node in self.database.select_all(MyTestNode):
            self.assertEqual(db_node.__dict__, rows[i].__dict__)
            i += 1



    def test_insert(self):
        # insert a row
        n = MyTestNode.create(UUID('31f40446-1565-4b2d-9f61-83e8b4dd5c95'), 'localhost', 4000)
        self.database.insert(n)

        # retrieve the row and check that it's has the same attribute
        self.assertEqual(self.database.select(MyTestNode, UUID('31f40446-1565-4b2d-9f61-83e8b4dd5c95')).__dict__, n.__dict__)


        #TODO: test duplicate insert, today a on_error will be fired, perhaps insert, replace would raise a exception insted








