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

import time

from test.test_case import OANTestCase
from oan.util import log
from oan.util.daemon_base import OANDaemonBase
from oan.network import serializer
from oan.network.server import OANServer, OANAuth
from oan.util.signal_handler import OANTerminateInterrupt

class MessageTest():
    def __init__(self, text = None):
        self.status = "ok"
        self.text = text

class ClientNodeDaemon(OANDaemonBase):
    def run(self):

        try:
            serializer.add(MessageTest)

            auth = OANAuth(
                'oand v1.0', '00000000-0000-code-1338-000000000000',
                'localhost', 1338, False
            )

            OANServer.error_callback = self.error_cb
            OANServer.start(auth)
            OANServer.push([('localhost', 1337)], [serializer.encode(MessageTest("Hello world"))])
            log.info("ClientNodeDaemon:run end")
            self.wait()

        except OANTerminateInterrupt:
            OANServer.shutdown()
            log.info("ClientNodeDaemon::run::OANTerminateInterrupt")
        except Exception, e:
            log.info("ClientNodeDaemon::run::Error %s" % e)
            OANServer.shutdown()


    def error_cb(self, url, messages):
        log.info("error_cb")
        time.sleep(0.1)
        OANServer.push([url], messages)

    def connect_cb(auth):
        pass



class TestOANListen(OANTestCase):
    # Remote node to test network against.
    daemon = None

    # Callback counters
    connect_counter = None
    message_counter = None
    close_counter = None

    def setUp(self):
        serializer.add(MessageTest)

        self.daemon = ClientNodeDaemon(
            pidfile="/tmp/ut_daemon.pid", stdout='/tmp/ut_out.log',
            stderr='/tmp/ut_err.log')

        self.daemon.start()

        self.connect_counter = 0
        self.message_counter = 0
        self.close_counter = 0

        self._auth = OANAuth(
            'oand v1.0', '00000000-0000-code-1337-000000000000', 'localhost',
            1337, False)


    def tearDown(self):
        pass
        #self.daemon.stop()

    def connect_cb(self, auth):
        log.info("connect_cb")
        self.connect_counter += 1

    def message_cb(self, auth, messages):
        log.info("message_cb %s" % messages)
        self.message_counter += len(messages)

    def close_cb(self, auth):
        log.info("close_cb")
        self.close_counter += 1

    def test_bridge(self):
        OANServer.connect_callback = self.connect_cb
        OANServer.message_callback = self.message_cb
        OANServer.close_callback = self.close_cb
        OANServer.start(self._auth)

        self.assertTrueWait(lambda : self.connect_counter == 1)
        self.assertTrueWait(lambda : self.message_counter == 1)
        log.info("Close bridge")
        OANServer.shutdown()

        self.assertTrueWait(lambda : self.close_counter == 1)


