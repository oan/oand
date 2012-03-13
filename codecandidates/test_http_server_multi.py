#!/usr/bin/env python

import requests
from time import sleep
import sys

from oan.util.daemon_base import OANDaemonBase
from oan.util.signal_handler import OANSignalHandler, OANTerminateInterrupt
from test.test_case import OANTestCase
from oan.network.http_server import OANHTTPServer

# Files used in test.
F_DWN="/tmp/oand_ut_http_daemon%s.down"
F_PID="/tmp/oand_ut_http_daemon%s.pid"
F_OUT="/tmp/oand_ut_http_daemon%s.out"
F_ERR="/tmp/oand_ut_http_daemon%s.err"

class TestDaemon(OANDaemonBase):
    port = None

    _status = None

    def inc_status(self, code):
        if code not in self._status:
            self._status[code] = 0
        self._status[code] += 1

    def run(self):
        http_server = OANHTTPServer(self.port)
        try:
            try:
                print "start: ", self.port
                while True:
                    OANSignalHandler.activate()

                    self._status = {}
                    for x in xrange(1,300):
                        try:
                            r = requests.get('http://localhost:%s/' % (8000 + x))
                            self.inc_status(r.status_code)
                        except Exception, e:
                            self.inc_status("Exception: %s" % type(e))
                    print self._status
                    sys.stdout.flush()

            finally:
                OANSignalHandler.deactivate()

        except OANTerminateInterrupt:
            pass
        finally:
            print "stop: ", self.port
            http_server.shutdown()
            f=open(F_DWN % self.port, "w")
            f.write("shutdown")
            f.close()

class TestHttpdServer(OANTestCase):
    _daemon = None

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_multi_deamon(self):
        daemon=[]
        for x in xrange(1,300):
            port = 8000 + x
            d = TestDaemon(F_PID % port, stdout=F_OUT % port, stderr=F_ERR % port)
            d.port = port
            d.start()
            daemon.append(d)

        # for d in daemon:
        #     d.stop()
