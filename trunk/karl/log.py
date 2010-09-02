from __future__ import with_statement

import logging
from logging.handlers import SysLogHandler
import os
import time

"""
Manages a logging utility that logs messages to a syslog, possibly located on
a remote host. Use of the logging facility is optional per Karl instance. If
no call to 'configure_log' is made, 'get_logger' will return a logger with a
null handler, effectively suppressing logging.
"""

LOG_NAME = 'karl.system'

def get_logger():
    logger = logging.getLogger(LOG_NAME)
    if not logger.handlers:
        logger.addHandler(NullHandler())
    return logger

def configure_log(**config):
    debug = config.get('debug', False)
    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logger = logging.getLogger(LOG_NAME)
    logger.setLevel(level)

    syslog_handler = None
    error_monitor_handler = None
    for old_handler in logger.handlers:
        if isinstance(old_handler, NullHandler):
            logger.removeHandler(old_handler)
        if isinstance(old_handler, KarlSysLogHandler):
            syslog_handler = old_handler
        if isinstance(old_handler, ErrorMonitorHandler):
            error_monitor_handler = old_handler

    if 'syslog' in config and syslog_handler is None:
        syslog = config.get('syslog')
        if ':' in syslog:
            host, port = syslog.split(':')
            port = int(port)
            address = (host, port)
        elif '/' in syslog:
            address = syslog
        else:
            address = (syslog, 514)

        app_name = config.get('syslog_app_name', 'karl')
        syslog_handler = KarlSysLogHandler(app_name, address)
        logger.addHandler(syslog_handler)

    if 'error_monitor_dir' in config and error_monitor_handler is None:
        error_monitor_handler = ErrorMonitorHandler(
            os.path.abspath(config['error_monitor_dir'])
        )
        logger.addHandler(error_monitor_handler)

def set_subsystem(subsystem):
    logger = get_logger()
    for handler in logger.handlers:
        if isinstance(handler, ErrorMonitorHandler):
            handler.set_subsystem(subsystem)

class KarlSysLogHandler(SysLogHandler):
    """
    Subclasses the Python standard library SysLogHandler in order to add an
    'app_name' to the formatted message.  In a situation where multiple Karls
    are logging to a single syslogd, this allows us to distinguish amongst
    Karl instances.
    """
    def __init__(self, app_name, address):
        SysLogHandler.__init__(self, address)
        self.app_name = app_name

    def format(self, record):
        formatted = SysLogHandler.format(self, record)
        return ' '.join((self.app_name, formatted))

class ErrorMonitorHandler(logging.Handler):
    """
    Provides a means of setting error status of arbitrary subsystems which can
    then be monitored by external observers.  The error states for all
    subsystems are stored in a single folder, with each subsystem represented
    by a single text format file.  The file is composed of N number of error
    entries separated by the keywork, 'ERROR' on a single line by itself.  The
    entries themselves are free format text.  Presence of error entries
    indicates to the monitoring service that the subsystem is in an error
    state.  The error state is cleared by removing all entries from the
    subsystem's file.
    """
    def __init__(self, path):
        logging.Handler.__init__(self, logging.ERROR)

        if not os.path.exists(path):
            os.makedirs(path)
        self.path = path
        self.file = None

    def set_subsystem(self, subsystem):
        self.file = os.path.join(self.path, subsystem)

    def emit(self, record):
        # Don't do anything if no subsystem is configured
        if self.file is None:
            return

        with open(self.file, 'a') as out:
            print >>out, 'ENTRY'
            print >>out, time.ctime()
            print >>out, self.format(record)

# Copied verbatim from Python logging documentation
class NullHandler(logging.Handler):
    def emit(self, record):
        pass

