#!/usr/bin/env python

import requests
from time import sleep

from oan.util.daemon_base import OANDaemonBase
from oan.util.signal_handler import OANSignalHandler, OANTerminateInterrupt
from test.test_case import OANTestCase
from oan.network.http_server import OANHTTPServer

# Files used in test.
F_DWN="/tmp/oand_ut_daemon.down"
F_PID="/tmp/oand_ut_daemon.pid"
F_OUT="/tmp/oand_ut_daemon.out"
F_ERR="/tmp/oand_ut_daemon.err"

class TestDaemon(OANDaemonBase):
    def run(self):
        http_server = OANHTTPServer(8000)
        while True:
            try:
                OANSignalHandler.wait()
            except OANTerminateInterrupt:
                break
            finally:
                http_server.shutdown()
                f=open(F_DWN, "w")
                f.write("shutdown")
                f.close()

class TestHttpdServer(OANTestCase):
    _daemon = None

    def setUp(self):
        self._daemon = TestDaemon(F_PID, stdout=F_OUT, stderr=F_ERR)
        self._daemon.start()

    def tearDown(self):
        self._daemon.stop()

    def test_get(self):
        r = requests.get('http://localhost:8000/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.text, 'Hello World!')

    def test_get_failed(self):
        self._daemon.stop()
        with self.assertRaises(requests.ConnectionError):
            requests.get('http://localhost:8000/')
        self._daemon.start()




