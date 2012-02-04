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

from oan.util.daemon_base import OANDaemonBase
from oan.util.decorator.capture import capture


class TestDaemon(OANDaemonBase):
    def run(self):
        while True:
            sys.stdout.write("This is stdout\n")
            sys.stderr.write("This is stderr\n")
            sys.stdout.flush()
            sys.stderr.flush()
            sleep(10)

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
    # Files used in test.
    pid="/tmp/oand_ut_daemon.pid"
    out="/tmp/oand_ut_daemon.out"
    err="/tmp/oand_ut_daemon.err"

    daemon = None

    def setUp(self):
        self.daemon = TestDaemon(self.pid, stdout=self.out, stderr=self.err)

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
        self.assertTrue(open(self.pid).readline().strip().isalnum())

        # Check if deamon is in running status.
        status = self.daemon.status()[0].strip()
        self.assertRegexpMatches(status, "oand (.*) is running...")

        self.daemon.stop()
        sleep(0.1)

        # Check if daemon stopped.
        self.test_stopped_status()

        # Check if pid file was removed.
        self.assertFalse(os.path.exists(self.pid))

    def test_deamon_already_started(self):
        self.daemon.start()
        # Give deamon time to start.
        sleep(0.1)

        # Start again to generate an error.
        status = self.daemon.start_error()[1].strip()
        self.assertEqual(
            status,
            "pidfile %s already exist. Daemon already running?" % self.pid
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
        open(self.out, "w").close()
        open(self.err, "w").close()
        sleep(0.1)

        self.daemon.start()

        # Let the deamon run for awhile, to create files.
        sleep(0.1)

        self.daemon.stop()
        sleep(0.1)

        #self.test_stopped_status()

        #self.assertTrue(open(self.pid).readline().strip().isalnum())
        self.assertTrue(open(self.out).readline().strip(), "This is stdout")
        self.assertTrue(open(self.err).readline().strip(), "This is stderr")

