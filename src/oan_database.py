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


from datetime import datetime, timedelta
from threading import Thread
from Queue import Queue

import time
import oan
import sqlite3
import uuid
import json

from oan import node_manager

'''
If we want to update database from more than one thread.

class OANDatabaseConnection(Thread):

    def __init__(self, db):
        super(OANDatabaseConnection, self).__init__()
        self.db=db
        self.reqs=Queue()
        self.start()

    def run(self):
        cnx = sqlite3.connect(self.db)
        cursor = cnx.cursor()
        while True:

            req, arg, res = self.reqs.get()
            if req=='--close--': break

            start = time.time()
            if isinstance(arg, list):
                cursor.executemany(req, arg)
            else:
                cursor.execute(req, arg)

            if res:
                for rec in cursor:
                    res.put(rec)

                res.put('--no more--')

            cnx.commit()
            elapsed = (time.time() - start)
            print "SQL:%f sec" % elapsed

        cnx.close()

    def execute(self, req, arg=None, res=None):
        self.reqs.put((req, arg or tuple(), res))

    def select(self, req, arg=None):
        res=Queue()
        self.execute(req, arg, res)
        while True:
            rec=res.get()
            if rec=='--no more--': break
            yield rec

    def close(self):
        self.execute('--close--')
'''

class OANDatabase:
    conn = None
    cursor = None
    tables = None

    def __init__(self, node):
        #self.conn = OANDatabaseConnection("%s%s.db" % (oan.VAR_DIR, node.uuid))
        self.conn = sqlite3.connect("%s%s.db" % (oan.VAR_DIR, node.uuid))
        self.cursor = self.conn.cursor()
        self.tables = {}

    def close(self):
        self.conn.close()

    def create(self, cls):
        if cls.__name__ not in self.tables:
            # check that the class as a uuid attribute

            self.cursor.execute("""
                create table if not exists %s (
                    uuid  BLOB primary key,
                    data  TEXT
                )
            """ % cls.__name__)

            self.tables[cls.__name__] = cls

    def insert(self, obj):
        self.insert_all((obj, ))

    def insert_all(self, objs):
        self._execute("insert", objs)

    def replace(self, obj):
        self.replace_all((obj, ))

    def replace_all(self, objs):
        self._execute("replace", objs)

    def delete(self, cls, uuid):
        self.create(cls)
        self.cursor.execute("delete from %s where uuid = ?" % (cls.__name__), (sqlite3.Binary(guid.bytes),))

    def delete_all(self, cls):
        self.cursor.execute("delete from %s" % (cls.__name__))

    def select(self, cls, guid):
        self.create(cls)
        self.cursor.execute("select uuid, data from %s where uuid = ?" % (cls.__name__), (sqlite3.Binary(guid.bytes),))
        self.cursor.fetchone()
        for pk, data in self.cursor():
            obj = cls(uuid.UUID(bytes=pk))
            obj.unserialize(json.loads(data))
            return obj

    def select_all(self, cls):
        self.create(cls)

        for pk, data in self.cursor.execute("select uuid, data from %s" % cls.__name__):
            obj = cls(uuid.UUID(bytes=pk))
            obj.unserialize(json.loads(data))
            yield obj

    def _execute(self, cmd, objs):
        cls = objs[0].__class__
        to_save = []
        for obj in objs:
            to_save.append(
                (sqlite3.Binary(obj.uuid.bytes), json.dumps(obj.serialize()))
            )

        self.create(cls)
        self.cursor.executemany("%s into %s (uuid, data) values (?, ?)" % (cmd, cls.__name__), to_save)

