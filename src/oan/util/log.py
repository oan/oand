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
import traceback
from time import gmtime, strftime

# Inherit all functionality from logging. util.log is like a
# sub module/class for logging.
from logging import *
import logging
import logging.handlers


# Loglevel that will not send any logging messages to log handler.
NONE = 100


# Number of tabs to indent message in log output.
indent = 0


# Gives shorter logging lines.
level_convert = {
    "DEBUG": "DBG",
    "INFO": "INF",
    "WARNING": "WAR",
    "ERROR": "ERR",
    "CRITICAL": "CRI",
    "Level 11": "TRA"
}


# Format of log output, used together with ContextFilter
FORMATTER="%(small_time)s %(small_levelname)-3s-%(process)d-%(threadName)-6s " \
          "%(extra)-50s %(indent)s%(message)s %(trace)s"


SYSLOG_FORMATTER="%(time)s %(hostname)s oand[%(process)d]: " \
                 "%(levelname)-8s %(message)s"


class ContextFilter(Filter):
    """Filter which injects contextual information into the log."""

    def filter(self, record):
        global indent
        record.hostname = os.uname()[1]
        record.time = strftime("%d %b %H:%M:%S", gmtime())
        record.small_time = strftime("%H:%M:%S", gmtime())
        record.small_levelname = level_convert[record.levelname]
        #record.levelname_ex = "[%s][%s]" % (record.levelname, record.threadName)

        record.indent ="."*indent
        # Text to display on debugging messages.
        record.extra = "(%s:%s:%s)" % (
            record.filename,
            record.funcName, record.lineno
        )

        #
        record.trace = ""
        if record.levelno == DEBUG+1:
            record.trace = "\n"
            for row in traceback.format_stack()[:-6]:
                record.trace += row

        return True


def setup(syslog_level = 100, stderr_level = 100, log_level = 100,
          file_name = None):
    """Setup all logging handlers"""
    _set_main_thread_name()

    my_logger = getLogger()
    my_logger.handlers = []

    # The logging filter will be done by the handlers. The general level will
    # log all everything.
    my_logger.setLevel(min(syslog_level, stderr_level, log_level))

    # Add information/tags that can be used on the log entries.
    f = ContextFilter()
    my_logger.addFilter(f)

    if syslog_level < 100:
        _setup_syslog(my_logger, syslog_level)

    if stderr_level < 100:
        _setup_stderr(my_logger, stderr_level)

    if file_name:
        _setup_file_log(my_logger, log_level, file_name)
    info("-----------------------------------------")

    info("Start logging.")


def trace(msg, *args, **kwargs):
    """
    Will store logginging information with traceback.

    """
    log(logging.DEBUG+1, msg, *args, **kwargs)


def _set_main_thread_name():
    """Set the name of the current (main) thread, for nicer logging."""
    import threading
    threading.current_thread().name="Main"


def _setup_syslog(my_logger, log_level):
    """Add syslog logging"""
    syslog_formatter = Formatter(SYSLOG_FORMATTER)

    handler = logging.handlers.SysLogHandler()
    handler.setLevel(log_level)
    handler.setFormatter(syslog_formatter)
    my_logger.addHandler(handler)


def _setup_stderr(my_logger, log_level):
    """Add stderr logging."""
    formatter = Formatter(FORMATTER)

    handler = StreamHandler()
    handler.setLevel(log_level)
    handler.setFormatter(formatter)
    my_logger.addHandler(handler)


def _setup_file_log(my_logger, log_level, file_name):
    """Add file logging"""
    formatter = Formatter(FORMATTER)

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
