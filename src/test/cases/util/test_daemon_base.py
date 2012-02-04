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
import signal
from time import sleep

from test.test_case import OANTestCase

from oan.util.daemon_base import OANDaemonBase
from oan.util.decorator.capture import capture

# Files used in test.
F_DWN="/tmp/oand_ut_daemon.down"
F_PID="/tmp/oand_ut_daemon.pid"
F_OUT="/tmp/oand_ut_daemon.out"
F_ERR="/tmp/oand_ut_daemon.err"


class TestDaemon(OANDaemonBase):

    def run(self):
        try:
            while True:
                sys.stdout.write("This is stdout\n")
                sys.stderr.write("This is stderr\n")
                sys.stdout.flush()
                sys.stderr.flush()
                sleep(10)
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


class TestLogging(OANTestCase):
    daemon = None

    def setUp(self):
        self.daemon = TestDaemon(F_PID, stdout=F_OUT, stderr=F_ERR)

    def tearDown(self):
        """Stop deamon in case any test fails."""
        self.daemon.stop()

    def test_stopped_status(self):
        status = self.daemon.status()[0].strip()
        self.assertEqual(status, "oand is stopped.")

    def test_deamon(self):
        self.daemon.start()
        # Give deamon time to start.
        sleep(0.1)

        # Check if deamon created pid file.
        self.assertTrue(open(F_PID).readline().strip().isalnum())

        # Check if deamon is in running status.
        status = self.daemon.status()[0].strip()
        self.assertRegexpMatches(status, "oand (.*) is running...")

        self.daemon.stop()
        sleep(0.1)

        # Check if daemon stopped.
        self.test_stopped_status()

        # Check if pid file was removed.
        self.assertFalse(os.path.exists(F_PID))

    def test_deamon_already_started(self):
        self.daemon.start()
        # Give deamon time to start.
        sleep(0.1)

        # Start again to generate an error.
        status = self.daemon.start_error()[1].strip()
        self.assertEqual(
            status,
            "pidfile %s already exist. Daemon already running?" % F_PID
        )

        self.daemon.stop()
        sleep(0.1)

    def test_restart(self):
        self.daemon.start()
        sleep(0.1)
        self.daemon.restart()
        sleep(0.1)
        self.daemon.stop()
        sleep(0.1)

        self.test_stopped_status()

    def test_daemon_run(self):
        open(F_OUT, "w").close()
        open(F_ERR, "w").close()
        sleep(0.1)

        self.daemon.start()

        # Let the deamon run for awhile, to create files.
        sleep(0.1)

        self.daemon.stop()
        sleep(0.1)

        #self.test_stopped_status()

        #self.assertTrue(open(F_PID).readline().strip().isalnum())
        self.assertTrue(open(F_OUT).readline().strip(), "This is stdout")
        self.assertTrue(open(F_ERR).readline().strip(), "This is stderr")

    def test_daemon_shutdown(self):
        if os.path.exists(F_DWN):
            os.remove(F_DWN)

        self.daemon.start()
        sleep(0.1)
        self.daemon.stop()
        sleep(0.1)

        self.assertTrue(open(F_DWN).readline().strip(), "shutdown")
