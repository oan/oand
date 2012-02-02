#!/usr/bin/env python
"""
Test cases for oan.statistic.py

"""

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"


from threading import Thread, Lock
import time
import sqlite3
from uuid import UUID
import json

import oan
from oan.util import log
from oan.passthru import OANPassthru


class OANDatabaseMessageExecute:
    _sql = None
    _arg = None

    @classmethod
    def create(cls, sql, arg = None):
        obj = cls()
        obj._sql = sql
        obj._arg = arg or tuple()
        return obj

    def execute(self, cursor):
        if isinstance(self._arg, list):
            cursor.executemany(self._sql, self._arg)
        else:
            cursor.execute(self._sql, self._arg)

    def __str__(self):
        return self._sql


class OANDatabaseMessageSelect:
    _sql = None
    _arg = None

    @classmethod
    def create(cls, sql, arg = None):
        obj = cls()
        obj._sql = sql
        obj._arg = arg or tuple()
        return obj

    def execute(self, cursor):
        cursor.execute(self._sql, self._arg)

        for rec in cursor:
            yield rec

    def __str__(self):
        return self._sql


class OANDatabaseMessageCreateTable:

    _table = None

    @classmethod
    def create(cls, table):
        obj = cls()
        obj._table = table
        return obj

    def execute(self, cursor):
        cursor.execute("""
            create table if not exists %s (
                oan_id  BLOB primary key,
                data  TEXT
            )
        """ % self._table)


class OANDatabaseMessageShutdown:

    def execute(self, cursor):
        pass


class OANDatabaseWorker(Thread):
    """

    """
    _pass = None
    _db_name = None

    def __init__(self, passthru, db_name):
        Thread.__init__(self)
        self.name = "Database-" + self.name
        self._pass = passthru
        self._db_name = db_name
        Thread.start(self)

    def run(self):
        q = self._pass
        log.info("Connecting to %s" % self._db_name)
        cnx = sqlite3.connect(self._db_name)
        cursor = cnx.cursor()

        log.info("Start database worker %s" % self.name)

        while True:
            (message, back) = q.get()
            start = time.time()
            try:
                ret = message.execute(cursor)
                self._pass.result(ret, back)
                if not isinstance(message, OANDatabaseMessageSelect):
                    cnx.commit()

            except Exception as ex:
                if not isinstance(message, OANDatabaseMessageSelect):
                    cnx.rollback()

                self._pass.error(message, ex, back, sys.exc_info())


            elapsed = (time.time() - start)
            log.debug("SQL: %f sec - %s" % (elapsed, message))

            if isinstance(message, OANDatabaseMessageShutdown):
                # Put back shutdown message for other worker threads
                q.execute(message)
                break

        cursor.close()
        cnx.close()
        log.info("Stop database worker %s" % self.name)


class OANDatabase:
    _config = None
    _worker = None
    _pass = None
    _tables = None
    _lock = None

    def __init__(self, config):
        self._config = config
        self._tables = {}
        self._lock = Lock()
        self._pass = OANPassthru()
        self._worker = OANDatabaseWorker(self._pass, "%s%s.db" % (oan.VAR_DIR, self._config.oan_id))

    def create(self, cls):
        with self._lock:
            if cls.__name__ not in self._tables:
                # check that the class as a oan_id attribute
                for status in self._pass.select(
                    OANDatabaseMessageCreateTable.create(cls.__name__)
                ):
                    pass

                self._tables[cls.__name__] = cls

    def insert(self, obj):
        self.insert_all((obj, ))

    def insert_all(self, objs):
        self._execute("insert", objs)

    def replace(self, obj):
        self.replace_all((obj, ))

    def replace_all(self, objs):
        self._execute("replace", objs)

    def count(self, cls):
        self.create(cls)
        for (num,) in self._pass.select(
            OANDatabaseMessageSelect.create(
                "select count(*) from %s" % (cls.__name__)
            )
        ):
            return num

        return 0

    def delete(self, cls, oid):
        self.create(cls)
        for status in self._pass.select(
            OANDatabaseMessageExecute.create(
                "delete from %s where oan_id = ?" % (cls.__name__),
                (sqlite3.Binary(oid.bytes),)
            )
        ):
            pass

    def delete_all(self, cls):
        self.create(cls)
        for status in self._pass.select(
            OANDatabaseMessageExecute.create("delete from %s" % (cls.__name__))
        ):
            pass

    def select(self, cls, guid):
        self.create(cls)
        for pk, data in self._pass.select(
            OANDatabaseMessageSelect.create(
                "select oan_id, data from %s where oan_id = ?" % (cls.__name__), (sqlite3.Binary(guid.bytes),)
            )
        ):
            obj = cls(UUID(bytes=pk))
            obj.unserialize(json.loads(data))
            return obj

    def select_all(self, cls):
        self.create(cls)

        for pk, data in self._pass.select(
           OANDatabaseMessageSelect.create("select oan_id, data from %s" % cls.__name__)
        ):
            obj = cls(UUID(bytes=pk))
            obj.unserialize(json.loads(data))
            yield obj

    def shutdown(self):
        self._pass.execute(OANDatabaseMessageShutdown())
        self._worker.join()

    def _execute(self, cmd, objs):
        to_save = []
        for obj in objs:
            to_save.append(
                (sqlite3.Binary(obj.oan_id.bytes), json.dumps(obj.serialize()))
            )

        cls = objs[0].__class__
        self.create(cls)

        # We do a select here beacuse we want to wait for the execute to
        # signal success or fail with a exception.
        # it needs a for statement to wait for the select yield.
        for status in self._pass.select(
           OANDatabaseMessageExecute.create("%s into %s (oan_id, data) values (?, ?)" % (cmd, cls.__name__), to_save)
        ):
            pass
