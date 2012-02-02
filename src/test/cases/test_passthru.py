#!/usr/bin/env python
'''
Test passthru

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import sys
from Queue import Queue
from threading import Thread

from test.test_case import OANTestCase
from oan.passthru import OANPassthru


class MockMessageShutdown(object):
    def execute(self, value):
        pass


class MessageNoExecute(object):
    pass


class MessageExecuteAddToQueue(object):
    value = None
    queue = None

    def __init__(self, queue, value):
        self.queue = queue
        self.value = value

    def execute(self, value):
        self.queue.put((self.value, value))


class MessageSelectAddToQueue(object):
    value = None
    queue = None

    def __init__(self, queue, value):
        self.queue = queue
        self.value = value

    def execute(self, value):
        self.queue.put((self.value, value))
        yield (self.value, value)
        yield (self.value, value)


class MessageSelectYieldAddToQueue(object):
    value = None
    queue = None

    def __init__(self, queue, value):
        self.queue = queue
        self.value = value

    def execute(self, value):
        self.queue.put(self.value)
        yield self.value


class MockWorker(Thread):
    _pass = None

    def __init__(self, passthru):
        Thread.__init__(self)
        self._pass = passthru
        Thread.start(self)

    def run(self):
        q = self._pass

        while True:
            if not q.empty():
                (message, back) = q.get()
                try:
                    ret = message.execute("I'll Put A Spell On You")
                    q.result(ret, back)
                except Exception as ex:
                    q.error(message, ex, back, sys.exc_info())
                finally:
                    q.task_done()
                if isinstance(message, MockMessageShutdown):
                    break


class TestOANPassthru(OANTestCase):
    queue = None
    passthru = None
    workers = None

    def setUp(self):
        self.queue = Queue()
        self.passthru = OANPassthru()
        self.workers = [MockWorker(self.passthru) for i in xrange(1)]

    def tearDown(self):
        self.queue.join()
        self.queue = None

        del self.passthru.on_error[:]
        del self.passthru.on_message[:]
        self.passthru.execute(MockMessageShutdown())
        self.passthru.join()
        self.passthru = None

        for worker in self.workers[:]:
            worker.join()
            self.workers.remove(worker)

    def on_error(self, message, exception):
        self.queue.put(message)

    def on_message(self, message):
        self.queue.put(message)

    def test_execute(self):
        """Test execute with standard parameters."""
        self.passthru.on_error.append(self.on_error)
        self.passthru.on_message.append(self.on_message)

        for i in xrange(10):
            self.passthru.execute(MessageExecuteAddToQueue(self.queue, i))

        for i in xrange(20):
            result = self.queue.get()
            if isinstance(result, tuple):
                (value1, value2) = result
                self.assertEqual(value1, i / 2)
                self.assertEqual(value2, "I'll Put A Spell On You")
            else:
                self.assertTrue(isinstance(result, MessageExecuteAddToQueue))
            self.queue.task_done()

        self.queue.join()
        self.assertTrue(self.passthru.empty())
        self.assertTrue(self.queue.empty())

    def test_execute_no_events(self):
        """Test execute without any events set."""
        self.passthru.execute(MessageNoExecute())
        self.passthru.join()

        self.assertTrue(self.passthru.empty())
        self.assertTrue(self.queue.empty())

    def test_execute_on_error(self):
        """Test execut with on_error."""
        self.passthru.on_error.append(self.on_error)

        for i in xrange(10):
            self.passthru.execute(MessageNoExecute())

        for i in xrange(10):
            message = self.queue.get()
            self.assertTrue(isinstance(message, MessageNoExecute))
            self.queue.task_done()

        self.queue.join()
        self.assertTrue(self.passthru.empty())
        self.assertTrue(self.queue.empty())

    def test_execute_on_message(self):
        """Test execut with on_error."""
        self.passthru.on_message.append(self.on_message)

        for i in xrange(10):
            self.passthru.execute(MessageNoExecute())

        for i in xrange(10):
            message = self.queue.get()
            self.assertTrue(isinstance(message, MessageNoExecute))
            self.queue.task_done()

        self.queue.join()
        self.assertTrue(self.passthru.empty())
        self.assertTrue(self.queue.empty())

    def test_select(self):
        """Test execute with standard parameters."""
        self.passthru.on_error.append(self.on_error)
        self.passthru.on_message.append(self.on_message)

        for i in xrange(10):
            result = self.passthru.select(MessageSelectAddToQueue(
                self.queue, i
            ))
            for value1, value2 in result:
                self.assertEqual(value1, i)
                self.assertEqual(value2, "I'll Put A Spell On You")

        for i in xrange(20):
            result = self.queue.get()
            if isinstance(result, tuple):
                (value1, value2) = result
                self.assertEqual(value1, i / 2)
                self.assertEqual(value2, "I'll Put A Spell On You")
            else:
                self.assertTrue(isinstance(result, MessageSelectAddToQueue))
            self.queue.task_done()

        self.queue.join()
        self.assertTrue(self.passthru.empty())
        self.assertTrue(self.queue.empty())

    def test_select_no_events(self):
        """Test select without any events set."""
        result = self.passthru.select(MessageNoExecute())
        with self.assertRaises(AttributeError):
            result.next()
        self.assertTrue(self.passthru.empty())
        self.assertTrue(self.queue.empty())

    def test_select_on_error(self):
        """Test select with on_error but no execute on message."""
        self.passthru.on_error.append(self.on_error)

        for i in xrange(10):
            result = self.passthru.select(MessageNoExecute())
            with self.assertRaises(AttributeError):
                result.next()

        for i in xrange(10):
            result = self.queue.get()
            self.assertTrue(isinstance(result, MessageNoExecute))
            self.queue.task_done()

        self.queue.join()
        self.assertTrue(self.passthru.empty())
        self.assertTrue(self.queue.empty())

    def test_select_on_message(self):
        """Test select with on_message but no execute on message."""
        self.passthru.on_message.append(self.on_message)

        for i in xrange(10):
            result = self.passthru.select(MessageNoExecute())
            with self.assertRaises(AttributeError):
                result.next()

        for i in xrange(10):
            result = self.queue.get()
            self.assertTrue(isinstance(result, MessageNoExecute))
            self.queue.task_done()

        self.queue.join()
        self.assertTrue(self.passthru.empty())
        self.assertTrue(self.queue.empty())

    def test_select_return(self):
        """Select "message" return a value."""
        result = self.passthru.select(MessageSelectYieldAddToQueue(
            self.queue, 47
        ))

        for val in result:
            self.assertEqual(val, 47)

        self.assertEqual(self.queue.get(), 47)
        self.queue.task_done()

        self.assertTrue(self.passthru.empty())
        self.assertTrue(self.queue.empty())
