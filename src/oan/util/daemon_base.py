#!/usr/bin/env python
"""
Test cases for util.daemon_base

Downloaded from
http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/

"""

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import sys, os, time, atexit
from signal import SIGTERM, SIGINFO, SIGINT

from oan.util.signal_handler import (OANSignalHandler, OANTerminateInterrupt,
    OANStatusInterrupt)

class OANDaemonBase:

    """
    A generic daemon class.

    Usage: subclass the Daemon class and override the run() method

    """
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile

    def daemonize(self):
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
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
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
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        file(self.pidfile,'w+').write("%s\n" % pid)

        return True

    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        """
        Start the daemon

        """
        # Check for a pidfile to see if the daemon already runs
        pid = self._pid_from_file(self.pidfile)

        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            return

        # Start the daemon
        if (self.daemonize()):
            OANSignalHandler.register(SIGINT, OANTerminateInterrupt())
            OANSignalHandler.register(SIGTERM, OANTerminateInterrupt())
            OANSignalHandler.register(SIGINFO, OANStatusInterrupt())
            self.run()
            sys.exit(0)

        #wait for the deamon to create the pid file.
        pid = self._get_pid_from_file(self.pidfile)
        if pid:
            pass
            #  print "Process started %s" % pid

    def stop(self):
        """
        Stop the daemon

        """
        pid = self._pid_from_file(self.pidfile)
        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return # not an error in a restart

        self._pid_terminate(pid)

    def restart(self):
        """
        Restart the daemon.

        """
        pid = self._pid_from_file(self.pidfile)
        if pid:
            self.stop()

        self.start()

    def status(self):
        """
        Stop of the daemon.

        """
        pid = self._pid_from_file(self.pidfile)

        if (pid):
            if (self._pid_is_running(pid)):
                print "oand (pid  %s) is running..." % pid
            else:
                print "oand dead but pid file exists"
        else:
            print "oand is stopped."

    def run(self):
        """
        You should override this method when you subclass Daemon. It will be
        called after the process has been daemonized by start() or restart().

        """

    def wait(self):
        """
        Waits for signals, terminate or user defined signal status.
        """
        OANSignalHandler.wait()


    def _get_pid_from_file(self, pidfile):
        for i in xrange(1, 40):
            pid = self._pid_from_file(pidfile)
            if pid:
                return pid

            #print "Waiting for %s" % pidfile
            time.sleep(i / 2)

        return None

    def _pid_from_file(self, pidfile):
        """ Get the pid from the pidfile """
        try:
            pf = file(pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        return pid


    def _pid_is_running(self, pid):
        """
        Check whether pid exists in the current process table.

        """
        import os, errno

        if pid < 0:
            return False
        try:
            os.kill(pid, 0)
        except OSError, e:
            return e.errno == errno.EPERM
        else:
            return True


    def _pid_terminate(self, pid):
        # Try killing the daemon process
        try:
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



