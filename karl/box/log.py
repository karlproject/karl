import contextlib
import datetime
import logging

from persistent.list import PersistentList


LEVELS = {
    logging.DEBUG: 'debug',
    logging.INFO: 'info',
    logging.WARNING: 'warning',
    logging.ERROR: 'error',
    logging.CRITICAL: 'critical',
}


class PersistentLog(PersistentList):

    def log(self, level, message, *args):
        """
        Store a logging entry in temporary volatile memory.
        """
        if args:
            message = message % args

        entry = {
            'timestamp': datetime.datetime.now(),
            'level': level,
            'message': message
        }

        if not hasattr(self, '_v_entries'):
            self._v_entries = []
        self._v_entries.append(entry)

    def save(self):
        """
        Save new logging entries to persistent list.
        """
        if hasattr(self, '_v_entries'):
            self.extend(self._v_entries)
            del self._v_entries


def get_log(community):
    log = getattr(community, 'archive_log', None)
    if log is None:
        community.archive_log = log = PersistentLog()
    return log


@contextlib.contextmanager
def persistent_log(community):
    logger = logging.getLogger('karl')
    handler = PersistentLogHandler(get_log(community))
    logger.addHandler(handler)
    yield handler.log
    logger.removeHandler(handler)


class PersistentLogHandler(logging.Handler):

    def __init__(self, log):
        super(PersistentLogHandler, self).__init__()
        self.log = log

    def emit(self,  record):
        self.log.log(record.levelname, record.msg, *record.args)
