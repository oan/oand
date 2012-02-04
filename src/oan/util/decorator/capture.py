"""
Decorator to capture stdout and stderr from a class method.

Example:

class Test():
    @capture
    def write(self):
        sys.stdout.write("This is stdout\n")
        sys.stderr.write("This is stderr\n")

test = Test()
stdout, stderr = test.write()

Read more:
    http://stackoverflow.com/questions/5136611/capture-stdout-from-a-script-in-python

"""

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import sys
from cStringIO import StringIO


def capture(f):
    """
    Decorator to capture stdout and stderr from a class method.

    """
    def captured(self, *args, **kw):

        # setup the environment
        stdout_backup = sys.stdout
        stderr_backup = sys.stderr

        try:
            # capture output
            sys.stdout = StringIO()
            sys.stderr = StringIO()
            f(self, *args, **kw)

            # release output
            stdout = sys.stdout.getvalue()
            stderr = sys.stderr.getvalue()
        finally:
            # close the stream
            sys.stdout.close()
            sys.stderr.close()
            # restore original stdout
            sys.stdout = stdout_backup
            sys.stderr = stderr_backup

        # captured output wrapped in a string
        return (stdout, stderr)

    return captured
