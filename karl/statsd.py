

class ZODBStatsdMonitor(object):
    # Implements the ActivityMonitor interface.

    def closedConnection(self, connection):
        client = statsd_client()
        database_name = connection.db().database_name or '_'
        loads, stores = connection.getTransferCounts(True)
        client.update_stats(['zodb.%s.loads' % database_name], loads)
        client.update_stats(['zodb.%s.stores' % database_name], stores)


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
            elapsed_ms = int(connection._setstate_elapsed * 1000.0)
            client.timing(stat, elapsed_ms)
            client.update_stats([stat], connection._setstate_count)
            connection._setstate_elapsed = 0.0
            connection._setstate_count = 0

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


def patch_repozitory():
    from repozitory.archive import Archive
    from repozitory.interfaces import IArchive
    for name in IArchive:
        setattr(Archive, name, metric(getattr(Archive, name)))
