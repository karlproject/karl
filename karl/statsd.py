
from decorator import decorator
from pystatsd.statsd import Client
import time


class NullStatsdClient(object):
    """No-op statsd client."""

    def timing(self, stat, time, sample_rate=1):
        pass

    def increment(self, stats, sample_rate=1):
        pass

    def decrement(self, stats, sample_rate=1):
        pass

    def update_stats(self, stats, delta, sample_rate=1):
        pass

    def send(self, data, sample_rate=1):
        pass


_client = NullStatsdClient()


def gauge(stat, value, sample_rate=1):
    """Send a gauge value to statsd.

    This really belongs in pystatsd, but pystatsd needs an update.
    """
    _client.send({stat: "%s|g" % value}, sample_rate)


def statsd_client():
    global _client
    return _client


def configure_statsd_client(host='localhost', port=8125):
    global _client
    _client = Client(host, port)


def metric_with_options(stats=None, sample_rate=1, count=True, timing=True):
    """Create a metric decorator with specific options."""

    def metric(f):
        """Decorator that sends function call statistics to statsd.

        Apply to functions or methods:

        @metric
        def foo():
            ...

        """
        if stats:
            if isinstance(stats, basestring):
                stat_names = [stats]
            else:
                stat_names = stats
        else:
            if hasattr(f, 'im_class'):
                to_decorate = f.im_func
                cls = f.im_class
                stat = '%s.%s.%s' % (cls.__module__, cls.__name__,
                                          f.__name__)
            else:
                to_decorate = f
                stat = '%s.%s' % (f.__module__, f.__name__)
            stat_names = [stat]

        def _call(func, *args, **kw):
            if count:
                _client.update_stats(stat_names, 1, sample_rate)

            if timing:
                start = time.time()
                try:
                    return func(*args, **kw)
                finally:
                    elapsed_ms = int((time.time() - start) * 1000)
                    for stat_name in stat_names:
                        _client.timing(stat_name, elapsed_ms, sample_rate)
            else:
                return func(*args, **kw)

        return decorator(_call, to_decorate)

    return metric


# 'metric' is the statsd metric decorator with default options.
metric = metric_with_options()


def once(f):
    """Decorator that calls a function once only; later calls are no-ops."""
    def call_once(func):
        if not deco.called:
            deco.called = True
            func()

    deco = decorator(call_once, f)
    deco.called = False
    return deco


class ZODBStatsdMonitor(object):
    # Implements the ActivityMonitor interface.

    def closedConnection(self, connection):
        client = statsd_client()
        database_name = connection.db().database_name or '_'
        loads, stores = connection.getTransferCounts(True)
        client.update_stats(['zodb.%s.loads' % database_name], loads)
        client.update_stats(['zodb.%s.stores' % database_name], stores)


@once
def patch_zodb():
    """Add a statsd ActivityMonitor to all ZODB DBs"""
    from ZODB.DB import DB
    DB._activity_monitor = ZODBStatsdMonitor()

    DB_open = DB.open
    DB_returnToPool = DB._returnToPool

    def report_pool_size(db):
        database_name = db.database_name or '_'
        stat = 'zodb.%s.pool' % database_name
        gauge(stat, len(db.pool.all))

    def open(self, *args, **kw):
        try:
            return DB_open(self, *args, **kw)
        finally:
            report_pool_size(self)

    def _returnToPool(self, connection):
        if connection.opened:
            client = statsd_client()
            database_name = self.database_name or '_'

            stat = 'zodb.%s.active' % database_name
            elapsed_ms = int((time.time() - connection.opened) * 1000.0)
            client.timing(stat, elapsed_ms)
            client.update_stats([stat], 1)

            stat = 'zodb.%s.setstates' % database_name
            elapsed_ms = int(self._setstate_elapsed * 1000.0)
            client.timing(stat, elapsed_ms)
            client.update_stats([stat], self._setstate_count)
            self._setstate_elapsed = 0.0
            self._setstate_count = 0

        try:
            DB_returnToPool(self, connection)
        finally:
            connection = None
            report_pool_size(self)

    DB.open = open
    DB._returnToPool = _returnToPool
    from ZODB.Connection import Connection
    Connection_setstate = Connection.setstate
    Connection._setstate_count = 0
    Connection._setstate_elapsed = 0.0

    def setstate(self, obj):
        start = time.time()
        try:
            return Connection_setstate(self, obj)
        finally:
            elapsed = time.time() - start
            self._setstate_count += 1
            self._setstate_elapsed += elapsed

    Connection.setstate = setstate


@once
def patch_relstorage():
    """Add metric decorators to certain RelStorage methods"""
    from relstorage.adapters.mover import ObjectMover

    changes = []
    for method_name in ObjectMover._method_names:
        for database_name in ('postgresql', 'mysql', 'oracle'):
            name = '%s_%s' % (database_name, method_name)
            method = getattr(ObjectMover, name)
            if method is not None:
                changes.append((name, metric(method)))

    for name, new_method in changes:
        setattr(ObjectMover, name, new_method)

    from relstorage.storage import RelStorage

    m = RelStorage._open_load_connection
    RelStorage._open_load_connection = metric(m)

    m = RelStorage._open_store_connection
    RelStorage._open_store_connection = metric(m)

    m = RelStorage._restart_load_and_poll
    RelStorage._restart_load_and_poll = metric(m)


@once
def patch_pgtextindex():
    from repoze.pgtextindex.index import PGTextIndex
    PGTextIndex._run_query = metric(PGTextIndex._run_query)
    PGTextIndex.index_doc = metric(PGTextIndex.index_doc)
    PGTextIndex.sort = metric(PGTextIndex.sort)


@once
def patch_repozitory():
    from repozitory.archive import Archive
    from repozitory.interfaces import IArchive
    for name in IArchive:
        setattr(Archive, name, metric(getattr(Archive, name)))


@once
def patch_all():
    patch_zodb()
    patch_relstorage()
    patch_pgtextindex()
    patch_repozitory()
