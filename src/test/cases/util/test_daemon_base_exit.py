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

import os
import sys
from time import sleep

from test.test_case import OANTestCase

from oan.util.daemon_base import OANDaemonBase
from oan.util.signal_handler import OANSignalHandler, OANTerminateInterrupt
from oan.util.decorator.capture import capture

# Files used in test.
F_DWN="/tmp/oand_ut_daemon.down"
F_PID="/tmp/oand_ut_daemon.pid"
F_OUT="/tmp/oand_ut_daemon.out"
F_ERR="/tmp/oand_ut_daemon.err"

class TestDaemon(OANDaemonBase):
    def run(self):
        f=open(F_DWN, "w")
        f.write("shutdown")
        f.close()

class TestDeamonExit(OANTestCase):

    def setUp(self):
        self.remove_files()

    def remove_files(self):
        if os.path.exists(F_DWN):
            os.remove(F_DWN)

        if os.path.exists(F_PID):
            os.remove(F_PID)

        if os.path.exists(F_OUT):
            os.remove(F_OUT)

        if os.path.exists(F_ERR):
            os.remove(F_ERR)

    def test_stop_already_exit(self):
        daemon = TestDaemon(F_PID, stdout=F_OUT, stderr=F_ERR)
        daemon.start()
        sleep(2)
        # the deamon run method have already exit.
        daemon.stop()
