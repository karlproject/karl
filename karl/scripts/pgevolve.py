"""Apply postgres schema evolutions
"""
from __future__ import print_function
import psycopg2
import sys

from karl.models import newtqbe
from karl.scripting import create_karl_argparser

class NonTransactional(str):
    pass

def main(argv=sys.argv):
    parser = create_karl_argparser(description=__doc__)
    parser.add_argument(
        '-g', '--generation', type=int,
        help="Schema generation to evolve to")
    parser.add_argument(
        '-l', '--latest', action='store_true',
        help="Evolve to the latest generation")

    args = parser.parse_args(sys.argv[1:])
    env = args.bootstrap(args.config_uri)

    root, registry = env['root'], env['registry']
    settings = registry.settings
    url = settings['repozitory_db_string']

    root._p_jar.close()
    evolver = KarlEvolver(url)
    if args.latest:
        args.generation = 999999999
    if args.generation is not None:
        evolver.evolve(args.generation)
    else:
        evolver.list()
    evolver.close()

class Evolver:

    def __init__(self, url):
        self.url = url
        self.conn = psycopg2.connect(url)
        self.cursor = cursor = self.conn.cursor()
        ex = cursor.execute
        ex("select from information_schema.tables"
           " where table_schema = 'public' AND table_name = %s",
           (self.table,))
        if not list(cursor):
            ex("create table %s (version int)"
               % self.table)
            ex("insert into %s values(-1)" % self.table)

        ex("select version from %s" % self.table)
        [[self.version]] = self.cursor
        self.conn.commit()

    def ex(self, sql, *args, **kw):
        self.cursor.execute(sql, args or kw)

    def ex1(self, sql, *args, **kw):
        self.conn.autocommit = True
        self.cursor.execute(sql, args or kw)
        self.conn.autocommit = False

    def query(self, sql, *args, **kw):
        self.ex(sql, *args, **kw)
        return list(self.cursor)

    def close(self):
        self.conn.close()

    def __iter__(self):
        version = self.version
        while True:
            version += 1
            try:
                yield version, getattr(self, 'evolve%s' % version)
            except AttributeError:
                return

    def _get_doc(self, evolver):
        if isinstance(evolver, tuple):
            return evolver[0]
        elif isinstance(evolver, NonTransactional):
            return evolver
        else:
            return evolver.__doc__.strip()

    def list(self):
        generations = list(self)
        if generations:
            print("Generations to be applied:\n")
            for version, evolve in generations:
                print(' ', version, self._get_doc(evolve))
            print("To evolve to a generation, use -g GENERATION")
        else:
            print("The database schema is up to date.")

    def evolve(self, target):
        for version, evolve in self:
            if version > target:
                break
            print('evolving', version, self._get_doc(evolve), end='...')
            sys.stdout.flush()
            if isinstance(evolve, tuple):
                for sql in evolve[1:]:
                    self.ex(sql)
            elif isinstance(evolve, NonTransactional):
                # Turn off autocommit to allow
                # statements that can't run in a transaction block
                self.conn.autocommit = True
                self.ex(evolve)
                self.conn.autocommit = False
            else:
                evolve()

            self.ex("update %s set version=%%s" % self.table, version)
            self.conn.commit()
            print("done")
            sys.stdout.flush()

###############################################################################

class KarlEvolver(Evolver):

    table = 'karl_schema_version'

    def evolve0(self):
        "Obsolete, NOOP"

    evolve1 = NonTransactional("DROP INDEX CONCURRENTLY newt_json_idx")
    evolve2 = NonTransactional("CREATE INDEX CONCURRENTLY newt_json_path_idx "
                               "ON newt USING GIN (state jsonb_path_ops)")

    def add_implemented_by(self):
        """Add (or re-add) implemented_by table for checking interfaces
        """
        from zope.interface import implementedBy
        self.ex("drop table if exists implemented_by")
        self.ex("""\
        create table implemented_by
          (class_name text, interface_name text,
           primary key (interface_name, class_name)
           )
        """)
        for (class_name, ) in self.query(
            "select distinct class_name from newt"
            ):
            module, name = class_name.rsplit('.', 1)
            try:
                module = __import__(module, {}, {}, ['*'])
            except ImportError:
                print("Can't import", module)
                continue

            try:
                class_ = getattr(module, name)
            except AttributeError:
                print("Can't get %s from %s" % (name, module.__name__))
                continue

            self.ex(
                "insert into implemented_by values " +  ", ".join(
                    "('%s', '%s.%s')" % (class_name, i.__module__, i.__name__)
                    for i in set(implementedBy(class_).flattened())
                    )
                )

        self.ex("analyze implemented_by");

    evolve3 = add_implemented_by

    evolve4 = ("Functions needed for profile recent items",
               newtqbe.interfaces_sql,
               newtqbe.can_view_sql)

    evolve5 = NonTransactional(*newtqbe.qbe.index_sql('interfaces'))

    def analyze(self):
        "analyze newt"
        self.ex("analyze newt")

    evolve6 = analyze

    evolve7 = ("Functions needed for community recent items",
               newtqbe.get_community_zoid_sql)
    evolve8 = NonTransactional(*newtqbe.qbe.index_sql('community'))
    evolve9 = analyze

    evolve10 = ("get_path(state)", newtqbe.get_path_sql)

    evolve11 = ("Update newt_can_view(state, principals)",
                newtqbe.can_view_sql)

    evolve12 = ("Drop object json and icontent_classes",
                "drop table if exists object_json, icontent_classes cascade")

    evolve13 = add_implemented_by # freshen occasionally :)
