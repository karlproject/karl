from perfmetrics import metricmethod
from repoze.lemonade.content import get_content_type
from repoze.pgtextindex.index import _missing
from repoze.pgtextindex.index import _truncate
from repoze.pgtextindex.index import SimpleWeightedText
from repoze.pgtextindex.interfaces import IWeightedText
import psycopg2
import random

from karl.utils import find_community
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

    def drop_and_create(self):
        cm = self.connection_manager
        conn = cm.connection
        cursor = cm.cursor
        try:
            # Create the table.
            stmt = """
            DROP TABLE IF EXISTS %(table)s;

            CREATE TABLE %(table)s (
                docid INTEGER NOT NULL PRIMARY KEY,
                community_docid varchar(100),
                content_type varchar(30),
                creation_date date,
                coefficient REAL NOT NULL DEFAULT 1.0,
                marker CHARACTER VARYING ARRAY,
                text_vector tsvector
            );

            CREATE INDEX %(table)s_index
                ON %(table)s
                USING gin(text_vector);

            CREATE INDEX %(table)s_community_docid_index
                ON %(table)s(community_docid);

            CREATE INDEX %(table)s_content_type_index
                ON %(table)s(content_type);

            CREATE INDEX %(table)s_creation_date_index
                ON %(table)s(creation_date);
            """ % self._subs
            cursor.execute(stmt)

            conn.commit()
        finally:
            cm.close()

    def _upsert(self, docid, params, text_vector_clause):
        """Update or insert a row in the index."""
        cursor = self.cursor
        kw = {'table': self.table, 'clause': text_vector_clause}
        for attempt in (1, 2, 3):
            stmt = """
            UPDATE %(table)s SET
                community_docid=%%s,
                content_type=%%s,
                creation_date=%%s,
                coefficient=%%s,
                marker=%%s,
                text_vector=%(clause)s
            WHERE docid=%%s
            """ % kw
            cursor.execute(stmt, tuple(params) + (docid,))
            if cursor.rowcount:
                # Success.
                return

            stmt = """
            SAVEPOINT pgtextindex_upsert;
            INSERT INTO %(table)s (docid, community_docid, content_type, creation_date,
            coefficient, marker, text_vector)
            VALUES (%%s, %%s, %%s, %%s, %%s, %%s, %(clause)s)
            """ % kw
            try:
                cursor.execute(stmt, (docid,) + tuple(params))
            except psycopg2.IntegrityError:
                # Another thread is working in parallel.
                # Wait a moment and try again.
                if attempt >= 3:
                    raise
                self.cursor.execute("ROLLBACK TO SAVEPOINT pgtextindex_upsert")
                self.sleep(attempt * random.random())
            else:
                # Success.
                cursor.execute('RELEASE SAVEPOINT pgtextindex_upsert')
                return

    @metricmethod
    def index_doc(self, docid, obj):
        """Add a document to the index.

        docid: int, identifying the document

        obj: The document to be indexed.

        The discriminator assigned to the index is used to extract a
        value from the document.  The value is either:

        - an object that implements IWeightedText, or

        - a string, or

        - a list or tuple of strings, which will be interpreted as weighted
          texts, with the default weight last, the A, B, and C weights
          first (if the list has enough strings), and other strings
          added to the default weight.

        return: None

        This can also be used to reindex documents.
        """
        # sql catalog fields
        content_params = _get_content_params(obj)

        if callable(self.discriminator):
            value = self.discriminator(obj, _missing)
        else:
            value = getattr(obj, self.discriminator, _missing)

        if value is _missing:
            # unindex the previous value
            self._index_null(docid, content_params)
            return None

        if isinstance(value, (list, tuple)):
            # Convert to a WeightedText.  The last value is always
            # a default text, then if there are other values, the first
            # value is assigned the A weight, the second is B, the third
            # is C, and the rest are assigned the default weight.
            abc = value[:-1][:3]
            kw = {'default': ' '.join(value[len(abc):])}
            value = SimpleWeightedText(*abc, **kw)

        clauses = []
        if IWeightedText.providedBy(value):
            coefficient = getattr(value, 'coefficient', 1.0)
            marker = getattr(value, 'marker', [])
            if isinstance(marker, basestring):
                marker = [marker]
            params = [coefficient, marker]
            text = '%s' % value  # Call the __str__() method
            if text:
                clauses.append('to_tsvector(%s, %s)')
                params.extend([self.ts_config,
                               _truncate(text, self.maxlen)])
            for weight in ('A', 'B', 'C'):
                text = getattr(value, weight, None)
                if text:
                    clauses.append('setweight(to_tsvector(%s, %s), %s)')
                    params.extend([self.ts_config,
                                   _truncate('%s' % text, self.maxlen),
                                   weight])

        else:
            # The value is a simple string.  Strings can not
            # influence the weighting.
            params = [1.0, []]
            if value:
                clauses.append('to_tsvector(%s, %s)')
                params.extend([self.ts_config,
                               _truncate('%s' % value, self.maxlen)])

        if len(params) > 2:
            params = content_params + params
            self._upsert(docid, params, ' || '.join(clauses))
        else:
            self._index_null(docid, content_params)

    reindex_doc = index_doc

    def _index_null(self, docid, content_params):
        params = content_params + ['0.0', []]
        self._upsert(docid, params, 'null')

    def get_sql_catalog_results(self, stmt):
        cursor = self.cursor
        cursor.execute(stmt)
        results = cursor.fetchall()
        return results

def _get_content_params(obj):
    community = find_community(obj)
    if community is not None:
        community = getattr(community, 'docid', None)

    try:
        content_type = get_content_type(obj)
        content_type = content_type.getName()
    except ValueError:
        content_type = obj.__class__.__name__

    try:
        creation_date = obj.created.isoformat()
    except AttributeError:
        creation_date = None

    return [community, content_type, creation_date]
