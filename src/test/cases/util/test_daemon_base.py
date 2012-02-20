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

import os
import sys
from time import sleep

from test.test_case import OANTestCase

from oan.util.daemon_base import OANDaemonBase, OANTerminateInterrupt
from oan.util.decorator.capture import capture

# Files used in test.
F_DWN="/tmp/oand_ut_daemon.down"
F_PID="/tmp/oand_ut_daemon.pid"
F_OUT="/tmp/oand_ut_daemon.out"
F_ERR="/tmp/oand_ut_daemon.err"


class TestDaemon(OANDaemonBase):

    def initialize(self):
        for x in xrange(1,10000):
            print "call", x

    def run(self):
        try:
            while True:
                sys.stdout.write("This is stdout\n")
                sys.stderr.write("This is stderr\n")
                sys.stdout.flush()
                sys.stderr.flush()
                self.wait()
        except OANTerminateInterrupt:
            pass
        finally:
            f=open(F_DWN, "w")
            f.write("shutdown")
            f.close()

    @capture
    def status(self):
        """Capture stdout and stderr to string"""
        OANDaemonBase.status(self)

    @capture
    def start_error(self):
        """Capture stdout and stderr to string"""
        OANDaemonBase.start(self)

    @capture
    def stop(self):
        """Capture stdout and stderr to string"""
        OANDaemonBase.stop(self)


class TestDeamonBase(OANTestCase):
    daemon = None

    def setUp(self):
        if os.path.exists(F_DWN):
            os.remove(F_DWN)

        if os.path.exists(F_PID):
            os.remove(F_PID)

        if os.path.exists(F_OUT):
            os.remove(F_OUT)

        if os.path.exists(F_ERR):
            os.remove(F_ERR)

        self.daemon = TestDaemon(F_PID, stdout=F_OUT, stderr=F_ERR)

    def tearDown(self):
        """Stop deamon in case any test fails."""
        self.daemon.stop()

    def is_stopped_status(self):
        status = self.daemon.status()[0].strip()
        self.assertEqual(status, "oand is stopped.")
        self.assertFalse(os.path.exists(F_PID))

    def is_running_status(self):
        status = self.daemon.status()[0].strip()
        self.assertRegexpMatches(status, "oand (.*) is running...")
        self.assertTrue(open(F_PID).readline().strip().isalnum())


    def test_deamon(self):
        self.daemon.start()
        self.is_running_status()
        self.daemon.stop()
        self.is_stopped_status()

    def test_deamon_already_started(self):
        self.daemon.start()
        # Give deamon time to start.

        # Start again to generate an error.
        status = self.daemon.start_error()[1].strip()
        self.assertEqual(
            status,
            "pidfile %s already exist. Daemon already running?" % F_PID
        )

        self.daemon.stop()

    def test_restart(self):
        self.daemon.start()
        self.is_running_status()
        self.daemon.restart()
        self.is_running_status()
        self.daemon.stop()
        self.is_stopped_status()

    def test_daemon_run(self):
        self.daemon.start()
        self.is_running_status()
        self.daemon.stop()
        self.is_stopped_status()

        self.assertTrue(open(F_OUT).readline().strip(), "This is stdout")
        self.assertTrue(open(F_ERR).readline().strip(), "This is stderr")

    def test_daemon_shutdown(self):
        self.daemon.start()
        self.is_running_status()
        self.daemon.stop()
        self.is_stopped_status()

        self.assertTrue(open(F_DWN).readline().strip(), "shutdown")
