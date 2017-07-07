"""Apply postgres schema evolutions
"""
from __future__ import print_function
import psycopg2
import sys

from karl.models import newtqbe
from karl.scripting import create_karl_argparser

class NonTransactional(str):
    pass

def main(url=None, latest=None, generation=None):
    if not url:
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
        latest = args.latest
        generation = args.generation
        root._p_jar.close()

    evolver = KarlEvolver(url)
    if latest:
        generation = 999999999
    if generation is not None:
        evolver.evolve(generation)
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
            if evolve is None:
                continue
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

skip = 'noop', 'select'

###############################################################################

class KarlEvolver(Evolver):

    table = 'karl_schema_version'

    def evolve0(self):
        "Obsolete, NOOP"

    evolve1 = NonTransactional("DROP INDEX CONCURRENTLY newt_json_idx")
    evolve2 = NonTransactional("CREATE INDEX CONCURRENTLY newt_json_path_idx "
                               "ON newt USING GIN (state jsonb_path_ops)")

    def add_interface_info(self):
        """Add (or re-add) implemented_by table for checking interfaces
        """
        from zope.interface import implementedBy
        self.ex("""\
        create table if not exists implemented_by
          (class_name text, interface_name text,
           primary key (interface_name, class_name)
           );
        truncate implemented_by;
        """)
        ifaces = set()
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

            class_ifaces = set(implementedBy(class_).flattened())
            ifaces.update(class_ifaces)

            self.ex(
                "insert into implemented_by values " +  ", ".join(
                    "('%s', '%s.%s')" % (class_name, i.__module__, i.__name__)
                    for i in class_ifaces
                    )
                )

        self.ex("analyze implemented_by");

        self.ex("""\
        create table if not exists interface_marker (
          interface_name text primary key,
          marker text);
        truncate interface_marker;
        """)

        for iface in ifaces:
            marker = iface.queryTaggedValue('marker')
            if marker:
                self.ex("insert into interface_marker"
                        " (interface_name, marker) values (%s, %s)",
                        '%s.%s' % (iface.__module__, iface.__name__), marker)

    evolve3 = add_interface_info

    evolve4 = ("Functions needed for profile recent items",
               newtqbe.interfaces_sql,
               newtqbe.can_view_sql)

    evolve5 = NonTransactional(*newtqbe.qbe.index_sql('interfaces'))

    def analyze(self):
        "analyze newt"
        self.ex("analyze newt")

    evolve6 = evolve7 = evolve8 = evolve9 = None

    evolve10 = ("get_path(state)", newtqbe.get_path_sql)

    evolve11 = ("Update newt_can_view(state, principals)",
                newtqbe.can_view_sql)

    evolve12 = ("Drop object json and icontent_classes",
                "drop table if exists"
                "  object_json, object_json_tid, icontent_classes"
                "  cascade")

    evolve13 = NonTransactional("drop index concurrently if exists"
                                " pgtextindex_community_docid_index")

    evolve14 = (
        "Set up trigger to populate community zoid",
        """
        create or replace function find_community_zoid(
          zoid_ bigint, class_name text, state jsonb)
          returns bigint
        as $$
        declare
          parent_class_name text;
          parent_state jsonb;
          parent_id bigint;
        begin
          if state is null then return null; end if;
          if class_name = 'karl.models.community.Community' then
             return zoid_;
          end if;
          parent_id := (state -> '__parent__' ->> '::=>')::bigint;
          if parent_id is null then return null; end if;
          select newt.class_name, newt.state from newt where zoid = parent_id
          into parent_class_name, parent_state;

          if parent_class_name is null then
            return null;
          end if;

          return find_community_zoid(
                    parent_id, parent_class_name, parent_state);
        end
        $$ language plpgsql;

        create or replace function populate_community_zoid_triggerf()
          returns trigger
        as $$
        declare
          new_zoid bigint;
          zoid bigint;
        begin
          new_zoid := NEW.state ->> 'community_zoid';
          zoid := find_community_zoid(
                    NEW.zoid, NEW.class_name, NEW.state)::text;

          if zoid is null then
             if new_zoid is not null then
               NEW.state := NEW.state - 'community_zoid';
             end if;
          else
            if new_zoid is null or zoid != new_zoid then
              NEW.state :=
                NEW.state || ('{"community_zoid": ' || zoid || '}')::jsonb;
            end if;
          end if;
          return NEW;
        end
        $$ language plpgsql;

        create trigger populate_community_zoid_trigger
          before insert or update
          on newt
          for each row
          execute procedure populate_community_zoid_triggerf();


        """)

    evolve15 = evolve16 = evolve17 = evolve18 = None

    evolve19 = (
        "Better find_community_zoid and simpler trigger function",
        """
        create or replace function find_community_zoid(
          zoid_ bigint, class_name text, state jsonb)
          returns bigint
        as $$
        declare
          parent_class_name text;
          parent_state jsonb;
          parent_id bigint;
        begin
          if state is null then return null; end if;
          if class_name = 'karl.models.community.Community' then
             return zoid_;
          end if;
          if state ? 'community_zoid' then
             return (state ->> 'community_zoid')::bigint;
          end if;
          parent_id := (state -> '__parent__' ->> '::=>')::bigint;
          if parent_id is null then return null; end if;
          select newt.class_name, newt.state from newt where zoid = parent_id
          into parent_class_name, parent_state;

          if parent_class_name is null then
            return null;
          end if;

          return find_community_zoid(
                    parent_id, parent_class_name, parent_state);
        end
        $$ language plpgsql STABLE;
        """)

    evolve20 = None

    def evolve21(self):
        """Add auxilary table for indexing data that crosses objects.

        Currently community_zoid.
        """
        self.ex("""
        create or replace function find_community_zoid(zoid_ bigint)
           returns bigint
        as $$
        declare
          res bigint;
        begin
          select find_community_zoid(zoid, class_name, state)
          from newt where zoid = zoid_ into res;
          return res;
        end
        $$ language plpgsql stable;

        create table karlex (zoid bigint primary key,
                             community_zoid bigint);

        insert into karlex (zoid, community_zoid)
        select zoid, find_community_zoid(zoid)
        from newt;

        create index karlex_community_zoid_idx on karlex (community_zoid);

        create or replace function populate_karlex_triggerf()
          returns trigger
        as $$
        begin
          NEW.community_zoid = find_community_zoid(NEW.zoid);
          return NEW;
        end
        $$ language plpgsql STABLE;

        CREATE TRIGGER populate_karlex_trigger
        BEFORE INSERT ON karlex FOR EACH ROW
        EXECUTE PROCEDURE populate_karlex_triggerf();
        """);

    evolve22 = (
        "Remove unnecessary triggers and indexes and add delete trigger",
        """
        drop function if exists notify_object_state_changed() cascade;
        drop function if exists populate_community_zoid_triggerf() cascade;
        drop index    if exists newt_community_idx;
        drop function if exists get_community_zoid(bigint, text, jsonb);

        create or replace function karlex_delete_on_state_delete()
          returns trigger
        as $$
        begin
          delete from karlex where zoid = OLD.zoid;
          return OLD;
        end;
        $$ language plpgsql;
        CREATE TRIGGER karlex_delete_on_state_delete_trigger
        AFTER DELETE ON object_state FOR EACH ROW
        EXECUTE PROCEDURE karlex_delete_on_state_delete();
        """)

    def evolve23(self):
        "Add auxilary table for indexing data that cross objects"
        self.ex(newtqbe.content_text())
        self.ex("""
        alter table karlex
          add column text tsvector,
          add column text_coefficient real;

        -- XXX Need to run special script in prod to avoid conflicts
        update karlex set text_coefficient = coefficient, text = text_vector
        from pgtextindex, newt
        where (state->>'docid')::int = docid
               and newt.zoid = karlex.zoid

        create index karlex_text_idx on karlex using gin (text);

        create or replace function populate_karlex_triggerf()
          returns trigger
        as $$
        begin
          NEW.text = content_text(NEW.zoid);
          NEW.text_coefficient = content_text_coefficient(NEW.zoid);
          NEW.community_zoid = find_community_zoid(NEW.zoid);
          return NEW;
        end
        $$ language plpgsql STABLE;
        """);
