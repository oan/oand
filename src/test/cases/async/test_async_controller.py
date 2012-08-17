#!/usr/bin/env python
"""
Test cases for oan.async.bridge

"""

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import asyncore
import os
from threading import Thread
from Queue import Queue

from test.test_case import OANTestCase
from oan.util import log
from oan.util.daemon_base import OANDaemonBase
from oan.util.signal_handler import OANTerminateInterrupt
from oan.util.decorator.synchronized import synchronized
from oan.async.server import OANListen
from oan.async.bridge import OANBridge, OANBridgeAuth
from oan.async import serializer

class OANAsyncController(asyncore.file_dispatcher):

    def __init__(self):
        self.r, self.w = os.pipe()
        self._in_buffer = ""
        asyncore.file_dispatcher.__init__(self, self.r)

    def writable(self):
        return False

    def handle_read(self):
        data = self.recv(1024)

        if data:
            self._in_buffer += data

            pos = self._in_buffer.find('\n')
            while pos > -1:
                cmd = self._in_buffer[:pos]
                self._in_buffer = self._in_buffer[pos+1:]

                log.info("OANAsyncController:handle_read: CMD[%s]" % (cmd))

                if cmd == "shutdown":
                    self.handle_close()

                pos = self._in_buffer.find('\n')

    def handle_close(self):
        self.close()

    def write_data(self, fd, str):
        total_count = 0
        num = len(str)
        while total_count < num:
            write_count = os.write(fd, str)

            if write_count > 0:
                total_count += write_count
                str = str[write_count:]
            else:
                log.info("write error")
                return None

    def shutdown(self):
        self.write_data(self.w, "shutdown\n")

    def notify(self):
        self.write_data(self.w, "notify\n")

class OANAsync:

    controller = None
    bridges = {}

    @staticmethod
    def start():
        OANAsync.controller = OANAsyncController()
        t = Thread(target=OANAsync.run, kwargs={})
        t.name="Loop"
        t.start()

    @staticmethod
    def run():
        log.info("Start OANAsync loop")
        asyncore.loop(timeout = 100000, use_poll = True, map = OANAsync.bridges, count = 1)
        log.info("Stop OANAsync loop")

    @staticmethod
    def shutdown():
        OANAsync.controller.shutdown()

    @staticmethod
    def notify():
        OANAsync.controller.notify()

class MessageTest():
    def __init__(self, text = None):
        self.status = "ok"
        self.text = text

class ServerNodeDaemon(OANDaemonBase):
    def run(self):
        try:
            serializer.add(MessageTest)
            auth = OANBridgeAuth.create(
                'oand v1.0', '00000000-0000-code-1338-000000000000',
                'localhost', 1338, False
            )
            listen = OANListen(auth)
            listen.accept_callback = self.accept
            listen.start()
            OANAsync.start()
            self.wait()

        except OANTerminateInterrupt:
            listen.shutdown()
            OANAsync.shutdown()

    def accept(self, bridge):
        log.info("ServerNodeDaemon::accept")
        bridge.message_callback = self.received

    def received(self, bridge, message):
        log.info("ServerNodeDaemon::received")
        if message.__class__.__name__ == 'MessageTest':
            bridge.send([MessageTest(message.text)])
            OANAsync.notify()


class TestOANBridge(OANTestCase):
    # Remote node to test network against.
    daemon = None

    # Callback counters
    connect_counter = None
    message_counter = None
    close_counter = None

    def setUp(self):
        serializer.add(MessageTest)

        self.daemon = ServerNodeDaemon(
            pidfile="/tmp/ut_daemon.pid", stdout='/tmp/ut_out.log',
            stderr='/tmp/ut_err.log')
        self.daemon.start()
        self.connect_counter = 0
        self.message_counter = 0
        self.close_counter = 0
        self._auth = OANBridgeAuth.create(
            'oand v1.0', '00000000-0000-code-1337-000000000000', 'localhost',
            1337, False)

    def tearDown(self):
        self.daemon.stop()

    def connect_cb(self, bridge, auth):
        self.connect_counter += 1

    def message_cb(self, bridge, message):
        if isinstance(message, MessageTest):
            self.message_counter += 1

    def close_cb(self, bridge):
        self.close_counter += 1

    def test_bridge(self):
        bridge = OANBridge("localhost", 1338, self._auth)
        self.assertTrue(bridge.readable())
        self.assertFalse(bridge.writable())

        bridge.connect_callback = self.connect_cb
        bridge.message_callback = self.message_cb
        bridge.close_callback = self.close_cb

        bridge.send([MessageTest("Hello world")])
        self.assertTrue(bridge.readable())
        self.assertTrue(bridge.writable())

        bridge.connect()
        OANAsync.start()

        import time
        for x in xrange(1,10):
            bridge.send([MessageTest("Hello world %s" % x)])
            OANAsync.notify()
            #time.sleep(1)

        #start_asyncore_loop(1)

        log.info(bridge.connected)
        log.info(self.connect_counter)
        log.info(self.message_counter)

        self.assertTrueWait(lambda : bridge.connected)
        self.assertTrueWait(lambda : self.connect_counter == 1)
        self.assertTrueWait(lambda : self.message_counter == 10)

        OANAsync.shutdown()
        bridge.shutdown()
        #self.assertTrueWait(lambda : self.close_counter == 1)
        #self.assertTrueWait(lambda : bridge.connected == False)
        #self.assertFalse(bridge.writable())
