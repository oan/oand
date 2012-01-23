#!/usr/bin/env python
'''
Logging setup for OAN.

This file replaces python logging.

Example:

    from oan.util import log
    log.setup("WARNING", "INFO", "DEBUG", '/tmp/oand.log', )
    log.debug("asf")

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import os
import types
import traceback
import logging
import logging.handlers
from logging import *
from time import gmtime, strftime

# Loglevel that will not send any logging messages to log handler.
NONE = 100

def setup(syslog_level, stderr_level, log_level, log_file_name):
    """Setup all logging handlers"""
    my_logger = getLogger()
    my_logger.handlers = []

    # The logging filter will be done by the handlers. The general level will
    # log all everything.
    my_logger.setLevel(0)

    # Add information/tags that can be used on the log entries.
    f = ContextFilter()
    my_logger.addFilter(f)

    _setup_syslog(my_logger, syslog_level)
    _setup_stderr(my_logger, stderr_level)
    _setup_file_log(my_logger, log_level, log_file_name)

def trace(msg, *args, **kwargs):
    """
    Will store logginging information with traceback.

    """
    log(logging.DEBUG+1, msg, *args, **kwargs)

class ContextFilter(Filter):
    """Filter which injects contextual information into the log."""

    def filter(self, record):
        record.hostname = os.uname()[1]
        record.time = strftime("%d %b %H:%M:%S", gmtime())
        record.levelname_ex = "[" + record.levelname + "]"

        # Text to display on debugging messages.
        if record.levelno == DEBUG:
            record.levelname_ex = "%s (%s - %s - %s:%s)" % (
                record.levelname_ex,
                record.threadName, record.filename,
                record.funcName, record.lineno
            )

        #
        record.trace = ""
        if record.levelno == DEBUG+1:
            record.trace = "\n"
            for row in traceback.format_stack()[:-6]:
                record.trace += row

        return True

def _setup_syslog(my_logger, log_level):
    """Add syslog logging"""
    syslog_formatter = Formatter(
        '%(time)s %(hostname)s oand[%(process)d]: %(levelname)-8s %(message)s'
    )

    handler = logging.handlers.SysLogHandler()
    handler.setLevel(log_level)
    handler.setFormatter(syslog_formatter)
    my_logger.addHandler(handler)

def _setup_stderr(my_logger, log_level):
    """Add stderr logging."""
    formatter = Formatter(
        '%(time)s %(levelname_ex)-9s %(message)s %(trace)s'
    )

    handler = StreamHandler()
    handler.setLevel(log_level)
    handler.setFormatter(formatter)
    my_logger.addHandler(handler)

def _setup_file_log(my_logger, log_level, file_name):
    """Add file logging"""
    formatter = Formatter(
        '%(time)s %(levelname_ex)-9s %(message)s %(trace)s'
    )
    handler = logging.handlers.RotatingFileHandler(
        file_name, maxBytes=2000000, backupCount=100
    )
    handler.setLevel(log_level)
    handler.setFormatter(formatter)
    my_logger.addHandler(handler)

if __name__ == '__main__':
    def main():
        setup(WARNING, 100, DEBUG, '/tmp/oand.log', )

        debug('This message should go to the log file')
        info('So should this')
        warning('And this, too')

    main()
