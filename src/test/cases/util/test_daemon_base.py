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
        while True:
            try:
                try:
                    OANSignalHandler.activate()
                    sys.stdout.write("This is stdout\n")
                    sys.stderr.write("This is stderr\n")
                    sys.stdout.flush()
                    sys.stderr.flush()
                    sleep(10000)
                finally:
                    OANSignalHandler.deactivate()

            except OANTerminateInterrupt:
                break
            finally:
                f=open(F_DWN, "w")
                f.write("shutdown")
                f.close()

    @capture
    def status(self):
        """Capture stdout and stderr to string."""
        OANDaemonBase.status(self)

    @capture
    def start_error(self):
        """Capture stdout and stderr to string."""
        OANDaemonBase.start(self)

    @capture
    def stop(self):
        """Capture stdout and stderr to string."""
        OANDaemonBase.stop(self)


class TestDeamonBase(OANTestCase):
    daemon = None

    def setUp(self):
        self.remove_files()
        self.daemon = TestDaemon(F_PID, stdout=F_OUT, stderr=F_ERR)

    def tearDown(self):
        """Stop deamon in case any test fails."""
        self.daemon.stop()

    def remove_files(self):
        if os.path.exists(F_DWN):
            os.remove(F_DWN)

        if os.path.exists(F_PID):
            os.remove(F_PID)

        if os.path.exists(F_OUT):
            os.remove(F_OUT)

        if os.path.exists(F_ERR):
            os.remove(F_ERR)

    def test_stopped_status(self):
        status = self.daemon.status()[0].strip()
        self.assertEqual(status, "oand is stopped.")
        self.assertFalse(os.path.exists(F_PID))

    def test_stopped_status_file_exists(self):
        with open(F_PID, "w") as f:
            f.write("777")

        status = self.daemon.status()[0].strip()
        self.assertEqual(status, "oand dead but pid file exists.")

        self.daemon.stop()

        # Check if daemon stopped.
        self.test_stopped_status()

    def test_running_status(self):
        # Check if deamon is in running status.
        self.assertFalse(self.daemon.is_alive())

        self.daemon.start()

        # Check if deamon created pid file.
        self.assertTrue(open(F_PID).readline().strip().isalnum())

        status = self.daemon.status()[0].strip()
        self.assertRegexpMatches(status, "oand (.*) is running...")
        self.assertTrue(open(F_PID).readline().strip().isalnum())

        self.daemon.stop()

        # Check if daemon stopped.
        self.test_stopped_status()

    def test_deamon(self):
        self.daemon.start()
        self.assertTrue(self.daemon.is_alive())
        self.daemon.stop()
        self.assertFalse(self.daemon.is_alive())

    def test_deamon_already_started(self):
        self.daemon.start()

        # Start again to generate an error.
        status = self.daemon.start_error()[1].strip()
        self.assertEqual(
            status,
            "pidfile %s already exist. Daemon already running?" % F_PID
        )

        self.daemon.stop()

    def test_restart(self):
        self.daemon.start()
        self.assertTrue(self.daemon.is_alive())
        self.daemon.restart()
        self.assertTrue(self.daemon.is_alive())
        self.daemon.stop()
        self.assertFalse(self.daemon.is_alive())

    def test_daemon_run(self):
        self.daemon.start()
        self.assertTrue(self.daemon.is_alive())
        self.daemon.stop()
        self.assertFalse(self.daemon.is_alive())

        self.assertTrue(open(F_OUT).readline().strip(), "This is stdout")
        self.assertTrue(open(F_ERR).readline().strip(), "This is stderr")

    def test_daemon_shutdown(self):
        self.daemon.start()
        self.assertTrue(self.daemon.is_alive())
        self.daemon.stop()
        self.assertFalse(self.daemon.is_alive())

        self.assertTrue(open(F_DWN).readline().strip(), "shutdown")
