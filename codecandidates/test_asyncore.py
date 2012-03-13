#!/usr/bin/env python
'''
Test cases for OAN, test communication between nodes

'''

__author__ = "martin.palmer.develop@gmail.com"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "martin.palmer.develop@gmail.com"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"


import asyncore
import socket
import os

from time import sleep, time
from datetime import datetime
from uuid import UUID
from Queue import Queue
from threading import Thread

from test.test_case import OANTestCase
from oan.util.daemon_base import OANDaemonBase
from oan.util.signal_handler import OANSignalHandler, OANTerminateInterrupt
from oan.event import OANEvent
from oan.passthru import OANPassthru

from oan.util.throttle import OANThrottle
from oan.util.thread import OANThread

class AsyncConnection(asyncore.dispatcher):


    def __init__(self, out_queue, connect_callback, received_callback, sent_callback, sock = None):
        asyncore.dispatcher.__init__(self, sock)
        self.out_queue = out_queue
        self.received_callback = received_callback
        self.sent_callback = sent_callback
        self.in_buffer = ""
        self.out_buffer = ""
        self.out_message = ""
        self.writable_count = 0

    def writable(self):
        if (self.writable_count % 1) == 0:
            print "writable", self.writable_count

        self.writable_count += 1

        return len(self.out_buffer) > 0 or not self.out_queue.empty()

    def handle_read(self):
        print "handle_read"
        data = self.recv(1024)
        if data:
            self.in_buffer += data

            pos = self.in_buffer.find('\n')
            while pos > -1:
                message = self.in_buffer[:pos]
                self.in_buffer = self.in_buffer[pos+1:]

                #print "CMD[%s]" % cmd
                self.received_callback(self, message)

                pos = self.in_buffer.find('\n')

    def handle_write(self):
        if not self.out_queue.empty():

            if self.out_message is not None:
                self.sent_callback(self, self.out_message)

            self.out_message = self.out_queue.get()

            if (self.out_message == None):
                self.handle_close()
                return
            else:
                self.out_buffer = "%s%s\n" % (self.out_buffer, self.out_message)

        sent = self.send(self.out_buffer)
        print "my sent number", sent, len(self.out_buffer)
        #if self.node is not None:
            #print "OUT[%s][%s]" % (self.node.oan_id, self.out_buffer[:sent])

        self.out_buffer = self.out_buffer[sent:]


    def handle_close(self):
        print "handle_close"
        asyncore.dispatcher.close(self)

    def handle_error(self):
        print "handle_error"
        asyncore.dispatcher.handle_error(self)
        self.handle_close()

    def send_message(self, message):
        self.send_callback(self, message)
        self.out_buffer = "%s%s%s" % (self.out_buffer, message, '\n')


class AsyncServer(asyncore.dispatcher):

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)

        self.on_received = OANEvent()
        self.on_sent = OANEvent()
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)
        print "listen"


    def handle_accept(self):
        print "handle_accept"
        try:
            pair = self.accept()
            if pair is None:
                return

            sock, addr = pair
            AsyncConnection(Queue(), self.received_callback, self.sent_callback, sock)
        except Exception, e:
            print e

    def received_callback(self, connection, message):
        print "push back", message
        connection.out_queue.put(message)

    def sent_callback(self, connection, message):
        pass


class AsyncClient():

    def __init__(self, out_queue, host, port):
        self.host = host
        self.port = port
        self.out_queue = out_queue
        self.on_received = OANEvent()
        self.on_sent = OANEvent()

    def connect(self):
        self.connection = AsyncConnection(self.out_queue, self.received_callback, self.sent_callback)
        self.connection.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((self.host, self.port))

    def received_callback(self, connection, message):
        print "received", message
        self.on_received(connection, message)

    def sent_callback(self, connection, message):
        print "send", message
        self.on_sent(connection, message)


class AsyncConnect:

    @classmethod
    def create(cls, client):
        obj = cls()
        obj.client = client
        return obj

    def execute(self):
        self.client.connect()


class AsyncListen:

    def create(cls, host, port):
        obj = cls()
        obj.host = host
        obj.port = port
        return obj

    def execute(self):
        AsyncServer(self.host, self.port)



class AsyncShutdown:
    @staticmethod
    def execute():
        pass

class AsyncServerDaemon(OANDaemonBase):

    def run(self):
        print "running..."
        AsyncServer("localhost", 8000)
        passthru = OANPassthru()
        worker = AsyncWorker(passthru)

        while True:
            try:
                self.wait()
            except OANTerminateInterrupt:
                break
            finally:
                pass

        worker.shutdown()

class AsyncClientDaemon(OANDaemonBase):

    port = None

    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        OANDaemonBase.__init__(self, pidfile, stdin, stdout, stderr)
        self.queue = Queue()

    def got_message(self, connection, message):
        print "got_message:" + message

    def run(self):
        try:
            AsyncServer("localhost", self.port)
            passthru = OANPassthru()
            worker = AsyncWorker(passthru)

            for x in xrange(1,10):
                out_queue = Queue()
                client = AsyncClient(out_queue, "localhost", 8000 + x)
                client.on_received.append(self.got_message)
                passthru.execute(AsyncConnect.create(client))
                out_queue.put("SEND [%s-%s]" % (self.port, 8000 + x))

            print "stopping"
            worker.shutdown()

            (utime, stime, cutime, cstime, elapsed_time) = os.times()
            print (utime, stime, cutime, cstime, elapsed_time)

        except OANTerminateInterrupt:
            pass
        except Exception, e:
            print e
        finally:
            pass


F_PID="/tmp/oand_ut_async.pid"
F_OUT="/tmp/oand_ut_async.out"
F_ERR="/tmp/oand_ut_async.err"

S_PID="/tmp/oand_ut_async_server.pid"
S_OUT="/tmp/oand_ut_async_server.out"
S_ERR="/tmp/oand_ut_async_server.err"

class AsyncWorker(OANThread):
    """
    Handles the main network loop.

    Polls the network passthru queue for new commands/messages that needs
    to be executed.

    Polls the network queue through asyncore for new connections and sends
    them internally in asyncore code to the OANListen object.

    Controll if OANNetworkTimer callbacks should be executed.

    """

    # Private variables
    _pass = None

    def __init__(self, passthru):
        OANThread.__init__(self)
        self.name = "NETW-" + self.name.replace("Thread-", "")

        self._pass = passthru
        self._timers = []
        Thread.start(self)



    def run(self):
        """Main network loop"""
        q = self._pass
        running = True

        while running:
            self.enable_shutdown()
            asyncore.loop(60, True, None, 1)
            self.disable_shutdown()
            try:
                while True:
                    (message, back) = q.get(True, 0.5 + OANThrottle.calculate(0.2))
                    print message
                    try:
                        ret = message.execute()
                        self._pass.result(ret, back)
                    except Exception as ex:
                        self._pass.error(message, ex, back)

                    if isinstance(message, AsyncShutdown):
                        running = False
                        break

            except Exception, e:
                print e
            finally:
                self.enable_shutdown()

    def shutdown(self):
        self._pass.execute(AsyncShutdown())
        self.join()

class TestAsyncore(OANTestCase):

    def setUp(self):
        pass
        self.server = AsyncServerDaemon(S_PID, stdout=S_OUT, stderr=S_ERR)
        self.server.start()

    def tearDown(self):
        pass
        #self.server.stop()

    def test_async_client(self):
        for x in xrange(1,300):
            self.client = AsyncClientDaemon("%s.%s" % (F_PID, x), stdout="%s.%s" % (F_OUT, x), stderr="%s.%s" % (F_ERR, x))
            self.client.start()
            print "started", x

