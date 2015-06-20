from karl.utils import get_setting

try:
    from repoze.pgtextindex import PGTextIndex
    postgres = True
except ImportError:
    PGTextIndex = object
    postgres = False

class KarlPGTextIndex(PGTextIndex):
    """
    Allows connection parameters to be provided at runtime rather than stored
    in the persistent object.
    """
    _v_dsn = None
    _v_table = None
    _v_ts_config = None
    _v_subs = None
    _v_maxlen = None
    _v_max_ranked = None

    def __init__(self, discriminator,
                 drop_and_create=False):
        if not postgres:
            raise NotImplementedError("repoze.pgtextindex must be installed.")

        if not callable(discriminator):
            if not isinstance(discriminator, basestring):
                raise ValueError('discriminator value must be callable or a '
                                 'string')

        self.discriminator = discriminator
        if drop_and_create:
            self.drop_and_create()

    @property
    def dsn(self):
        dsn = self._v_dsn
        if dsn is None:
            dsn = get_setting(self, 'pgtextindex.dsn')
            if dsn is None:
                raise ValueError("Missing setting: pgtextindex.dsn")
            self._v_dsn = dsn
        return dsn

    @property
    def table(self):
        table = self._v_table
        if table is None:
            table = get_setting(self, 'pgtextindex.table', 'pgtextindex')
            self._v_table = table
        return table

    @property
    def ts_config(self):
        ts_config = self._v_ts_config
        if ts_config is None:
            ts_config = get_setting(self, 'pgtextindex.ts_config', 'english')
            self._v_ts_config = ts_config
        return ts_config

    @property
    def _subs(self):
        subs = self._v_subs
        if subs is None:
            subs = dict(table=self.table)
            self._v_subs = subs
        return subs

    @property
    def maxlen(self):
        maxlen = self._v_maxlen
        if maxlen is None:
            # Set a low value to prevent so much TOAST retrieval of
            # big data on every prefix search for relevance ranking
            maxlen = int(get_setting(self, 'pgtextindex.maxlen', 44000))
            self._v_maxlen = maxlen
        return maxlen

    @property
    def max_ranked(self):
        max_ranked = self._v_max_ranked
        if max_ranked is None:
            max_ranked = int(get_setting(self, 'pgtextindex.max_ranked', 6000))
            self._v_max_ranked = max_ranked
        return max_ranked
