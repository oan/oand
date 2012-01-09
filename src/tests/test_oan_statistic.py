#!/usr/bin/env python
'''
Test cases for oan_statistic.py

'''

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from oan_unittest import OANTestCase

from datetime import datetime, timedelta

import unittest
import time
import oan
import uuid
import json

from oan import node_manager
from oan_loop import OANLoop
from oan_event import OANEvent

from oand import OANApplication
from oan_config import OANConfig
from oan_node_manager import OANNetworkNode, OANNodeManager
from oan_message import OANMessagePing, OANMessageHeartbeat, OANMessageClose, OANMessageHandshake

from Queue import Queue
from oan_database import OANDatabase

'''
from bson.binary import Binary, UUIDLegacy

from bson.binary import Binary, UUIDLegacy
>>> id = uuid.uuid4()
>>> db.test.insert({'uuid': Binary(id.bytes, 3)})
ObjectId('...')
>>> db.test.find({'uuid': id}).count()
0
>>> db.test.find({'uuid': UUIDLegacy(id)}).count()
1
>>> db.test.find({'uuid': UUIDLegacy(id)})[0]['uuid']
UUID('...')
>>>
>>> # Convert from subtype 3 to subtype 4
>>> doc = db.test.find_one({'uuid': UUIDLegacy(id)})
>>> db.test.save(doc)
ObjectId('...')
>>> db.test.find({'uuid': UUIDLegacy(id)}).count()
0
>>> db.test.find({'uuid': {'$in': [UUIDLegacy(id), id]}}).count()
1
>>> db.test.find_one({'uuid': id})['uuid']
'''



'''
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

class TestOANStatistic(OANTestCase):
    queue = None
    app = None

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_sqllite(self):

        l = []
        for i in xrange(10000):
            l.append(MyTestNode.create(uuid.uuid4(), 'localhost', i))

        database = OANDatabase()
        database.insert_all(l)

        counter = 0
        for n in database.select_all(MyTestNode):
            counter = counter + 1
            print counter, n

    def atest_mongodb(self):
        #connect to mongodb
        connection = Connection('localhost', 27017)

        # get database
        db = connection.oan_statistic

        # get a collection / table
        collection = db.oan_network_node_statistic

        collection.drop()

        n1 = uuid.UUID('fa587853-4511-4a11-ba23-e56a3cc7ead2')
        n2 = uuid.UUID('fa587853-4511-4a11-ba23-e56a3cc7ead2')

        post = {"_id":  Binary(n1.bytes, 3),
                "text": "My first blog posssssdfasdfsssssst!",
                "tags": ["mongodb", "python", "pymongo"],
                "date": datetime.utcnow()}

        collection.save(post)

        print collection.find_one({"_id": Binary(n1.bytes, 3)})

        for post in collection.find():
            print post


        collection.drop_indexes()


'''









