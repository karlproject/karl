import logging
from logging.handlers import SysLogHandler

"""
Manages a logging utility that logs messages to a syslog, possibly located on
a remote host.  Use of the logging facility is optional per Karl instance.  If
no call to 'setup_log' is made, 'get_logger' will return a logger with a null
handler, effectively suppressing logging.
"""

LOG_NAME = 'karl.system'

def get_logger():
    logger = logging.getLogger(LOG_NAME)
    if not logger.handlers:
        logger.addHandler(NullHandler())
    return logger

def setup_log(app_name, address, level):
    logger = logging.getLogger(LOG_NAME)
    logger.setLevel(level)
    for old_handler in logger.handlers:
        logger.removeHandler(old_handler)
    handler = KarlSysLogHandler(app_name, address)
    logger.addHandler(handler)

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

# Copied verbatim from Python logging documentation
class NullHandler(logging.Handler):
    def emit(self, record):
        pass

