#!/usr/bin/env python
"""
Test cases for util.daemon_base

Based on 
http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/

"""

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import sys
import os
import time
import atexit
import errno
from signal import SIGTERM, SIGINFO, SIGINT

from oan.util.signal_handler import (
    OANSignalHandler, OANTerminateInterrupt, OANStatusInterrupt
)

class OANDaemonBase:
    """
    A generic daemon class.

    Usage: subclass the Daemon class and override the run() method

    """
    stdin = None
    stdout = None
    stderr = None
    pidfile = None

    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile

    def run(self):
        """
        You should override this method when you subclass the Daemon. It will
        be called after the process has been daemonized by start or restart.

        """

    def start(self):
        """Start the daemon."""
        if self.is_alive():
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            return

        # Start the daemon
        if self._daemonize():
            self._register_signal()
            self.run()
            sys.exit(0)
        else:
            self._wait_for_deamon_to_start()

    def stop(self):
        """Stop the daemon"""
        if not self.is_alive():
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return
        else:
            self._pid_terminate()
            self._wait_for_deamon_to_stop()

    def restart(self):
        """Restart the daemon."""
        if self.is_alive():
            self.stop()

        self.start()

    def status(self):
        """Status of the daemon."""
        if self.is_alive():
            if (self._pid_is_running()):
                print "oand (pid  %s) is running..." % self._get_pid()
            else:
                print "oand dead but pid file exists."
        else:
            print "oand is stopped."

    def is_alive(self):
        """
        Returns true if the deamon is alive (pid-file exist).

        This methods returns True just before the run() method starts until
        just after the run() method terminates.

        """
        return self._get_pid()

    def wait(self):
        """Waits for signals, terminate or user defined signal status."""
        OANSignalHandler.wait()

    def _daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16

        """
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                return False
        except OSError, e:
            sys.stderr.write(
                "fork #1 failed: %d (%s)\n" % (e.errno, e.strerror)
            )
            sys.exit(1)

        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write(
                "fork #2 failed: %d (%s)\n" % (e.errno, e.strerror)
            )
            sys.exit(1)

        self._redirect_standard_file_descriptors()
        self._create_pid()

        return True

    def _redirect_standard_file_descriptors(self):
        """Redirect stdin/stdout/stderr for deamon to file."""
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

    def _create_pid(self):
        """Create pid file and make sure it's deleted when app exists."""
        atexit.register(self._delpid)
        pid = str(os.getpid())
        file(self.pidfile,'w+').write("%s\n" % pid)

    def _delpid(self):
        """Delete pid file."""
        os.remove(self.pidfile)

    def _wait_for_deamon_to_start(self):
        """
        Wait for deamon to start (pid file to be created.)

        Between each check of the existens of the pid file, wait between 0.5
        and 20 seconds.

        """
        self._get_pid_wait()

    def _wait_for_deamon_to_stop(self):
        """
        Wait for deamon to stop (pid file to be deleted.)

        Between each check of the existens of the pid file, wait between 0.5
        and 20 seconds.

        """
        for i in xrange(1, 40):
            pid = self._get_pid()
            if not pid:
                return

            time.sleep(i / 2)

    def _get_pid_wait(self):
        """
        Get the daemon pid from the pidfile, wait until it's created.

        Between each check of the existens of the pid file, wait between 0.5
        and 20 seconds.

        """
        for i in xrange(1, 40):
            pid = self._get_pid()
            if pid:
                return pid

            time.sleep(i / 2)

        return None

    def _get_pid(self):
        """Get the daemon pid from the pidfile if it exists."""
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        return pid

    def _pid_is_running(self):
        """Check whether pid exists in the current process table."""
        pid = self._get_pid()
        if pid < 0:
            return False
        try:
            os.kill(pid, 0)
        except OSError, e:
            return e.errno == errno.EPERM
        else:
            return True

    def _register_signal(self):
        """Register signals used by Deamon"""
        OANSignalHandler.register(SIGINT, OANTerminateInterrupt())
        OANSignalHandler.register(SIGTERM, OANTerminateInterrupt())
        OANSignalHandler.register(SIGINFO, OANStatusInterrupt())

    def _pid_terminate(self):
        """Kill the daemon process."""
        try:
            pid = self._get_pid()
            for i in xrange(1,40):
                os.kill(pid, SIGTERM)
                #print "Waiting for process to terminate (%s)" % pid
                time.sleep(i/2)

        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
