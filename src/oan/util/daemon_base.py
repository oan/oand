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
from signal import SIGTERM, signal

class OANSigtermError(Exception): """Raised in run when program is stopped."""


class OANDaemonBase:
    stdin = None
    stdout = None
    stderr = None
    pidfile = None

    """
    A generic daemon class.

    Usage: subclass the Daemon class and override the run() method

    """
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile


    def start(self):
        """
        Start the daemon

        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            return

        # Start the daemon
        if (self._daemonize()):
            self._register_signal()
            self.run()
            sys.exit(0)
        else:
            # Wait for the deamon to start
            while(not self.is_alive()):
                pass

    def stop(self):
        """
        Stop the daemon

        """
        # Get the pid from the pidfile
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return # not an error in a restart

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)

        # Wait for the deamon to stop
        while(self.is_alive()):
            pass

    def restart(self):
        """
        Restart the daemon.

        """
        self.stop()
        self.start()

    def status(self):
        """
        Status of the daemon.

        """
        pid = self._get_pid()
        if (pid):
            if (self._pid_exists(pid)):
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

    def is_alive(self):
        """
        Returns whether the deamon is alive.

        This methods returns True jsut before the run() method starts until
        just after the run() method terminates.

        """
        return self._get_pid()

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
        atexit.register(self._delpid)
        pid = str(os.getpid())
        file(self.pidfile,'w+').write("%s\n" % pid)

        return True

    def _delpid(self):
        os.remove(self.pidfile)

    def _get_pid(self):
        """
        Get the daemon pid from the pidfile if exists.

        """
        pid = None
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        return pid

    def _pid_exists(self, pid):
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

    @staticmethod
    def _shutdown(signum, frame):
        def no_signal(signum, frame):
            pass

        signal(SIGTERM, no_signal)
        raise OANSigtermError()

    def _register_signal(self):
        signal(SIGTERM, self._shutdown)

