#!/usr/bin/env python
"""
Test cases for util.daemon_base.

"""

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from time import sleep

from test.test_case import OANTestCase
from oan.util.daemon_base import OANDaemonBase
from oan.util import log

# Files used in test.
F_DWN="/tmp/ut_daemon.down"
F_PID="/tmp/ut_daemon.pid"
F_OUT="/tmp/ut_daemon.out"
F_ERR="/tmp/ut_daemon.err"

class TestDaemon(OANDaemonBase):
    def run(self):
        f=open(F_DWN, "w")
        f.write("shutdown")
        f.close()
        log.info("run method")

class TestDeamonExit(OANTestCase):

    def setUp(self):
        self.init_files()

    def init_files(self):
        open(F_DWN, "w").close()
        open(F_PID, "w").close()
        open(F_OUT, "w").close()
        open(F_ERR, "w").close()

    def test_stop_already_exit(self):
        daemon = TestDaemon(F_PID, stdout=F_OUT, stderr=F_ERR)
        daemon.start()
        sleep(2)
        # the deamon run method have already exit.
        daemon.stop()
