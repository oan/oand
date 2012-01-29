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
                    q.error(message, ex, back)
                finally:
                    q.task_done()
                if isinstance(message, MockMessageShutdown):
                    break


class TestOANPassthru(OANTestCase):
    queue = None
    passthru = None
    worker = None

    def setUp(self):
        self.queue = Queue()
        self.passthru = OANPassthru()
        self.worker = MockWorker(self.passthru)

    def tearDown(self):
        self.queue.join()
        self.queue = None

        del self.passthru.on_error[:]
        del self.passthru.on_message[:]
        self.passthru.execute(MockMessageShutdown())
        self.passthru.join()
        self.passthru = None

        self.worker.join()
        self.worker = None

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









# Test with more workers and passthru at the same time.
# pep8 pylint
