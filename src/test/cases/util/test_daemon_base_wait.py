#!/usr/bin/env python
"""
Test cases for util.daemon_base

"""

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from oan.util.signal_handler import OANTerminateInterrupt, OANStatusInterrupt

from test_daemon_base import (
    TestDaemon, TestDeamonBase, F_DWN, F_PID, F_OUT, F_ERR
)


class TestDaemonWait(TestDaemon):
    def run(self):
        while True:
            try:
                self.wait()

            except OANStatusInterrupt, e:
                print e
            except OANTerminateInterrupt, e:
                break
            finally:
                f=open(F_DWN, "w")
                f.write("shutdown")
                f.close()


class TestDeamonBaseWait(TestDeamonBase):
    daemon = None

    def setUp(self):
        self.remove_files()
        self.daemon = TestDaemon(F_PID, stdout=F_OUT, stderr=F_ERR)
