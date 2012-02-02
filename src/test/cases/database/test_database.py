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

from uuid import UUID, uuid4

from test.test_case import OANTestCase
from oan.config import OANConfig
from oan.database.database import OANDatabase

class MyTestNode():
    oan_id = None
    host = None
    port = None

    def __init__(self, oan_id):
        self.oan_id = oan_id

    @classmethod
    def create(cls, oan_id, host, port):
        obj = cls(oan_id)
        obj.host, obj.port = host, port
        return obj

    def unserialize(self, data):
        self.host, self.port = data

    def serialize(self):
        return(self.host, self.port)

    def __str__(self):
        return 'MyTestNode(%s, %s, %s)' % (self.oan_id, self.host, self.port)

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

        #Test exception with get method
        with self.assertRaises(Exception):
            self.database.insert(n)




    def test_insert_all(self):
        # Insert rows
        rows = self.generate_nodes()
        self.database.insert_all(rows)

        # retrieve the rows and check that it's has the same attribute
        i = 0
        for db_node in self.database.select_all(MyTestNode):
            self.assertEqual(db_node.__dict__, rows[i].__dict__)
            i += 1

        #Test exception with get method
        with self.assertRaises(Exception):
            self.database.insert_all(rows)




    def test_replace(self):
        # insert a row
        n = MyTestNode.create(UUID('31f40446-1565-4b2d-9f61-83e8b4dd5c95'), 'localhost', 4000)
        self.database.insert(n)

        # retrieve the row and check that it's has the same attribute
        self.assertEqual(self.database.select(MyTestNode, UUID('31f40446-1565-4b2d-9f61-83e8b4dd5c95')).__dict__, n.__dict__)

        # change a attribute and replace the node in database
        n.host = 'replace_host'
        self.database.replace(n)

        # retrieve and check if the host has changed
        self.assertEqual(self.database.select(MyTestNode, UUID('31f40446-1565-4b2d-9f61-83e8b4dd5c95')).host, 'replace_host')




    def test_replace_all(self):
        # Insert rows
        rows = self.generate_nodes()
        self.database.insert_all(rows)

        # retrieve the rows and check that it's has the same attribute
        i = 0
        for db_node in self.database.select_all(MyTestNode):
            self.assertEqual(db_node.__dict__, rows[i].__dict__)
            i += 1


        rows[7].host = "replace_host_1"
        rows[20].host = "replace_host_2"
        rows[221].host = "replace_host_3"

        self.database.replace_all(rows)

        rows_from_db = []
        for db_node in self.database.select_all(MyTestNode):
            rows_from_db.append(db_node)

        self.assertEqual(rows_from_db[7].host, 'replace_host_1')
        self.assertEqual(rows_from_db[20].host, 'replace_host_2')
        self.assertEqual(rows_from_db[221].host, 'replace_host_3')

