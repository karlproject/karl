"""Apply postgres schema evolutions
"""
from __future__ import print_function
import psycopg2
import sys

from karl.scripting import create_karl_argparser

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

    def list(self):
        generations = list(self)
        if generations:
            print("Generations to be applied:\n")
            for version, evolve in generations:
                print(' ', version, evolve.__doc__)
            print("To evolve to a generation, use -g GENERATION")
        else:
            print("The database schema is up to date.")

    def evolve(self, target):
        for version, evolve in self:
            if version > target:
                break
            if isinstance(evolve, tuple):
                print('evolving', version, evolve[0], end='...')
                sys.stdout.flush()
                if len(evolve) == 2:
                    # single sql. Turn off autocommit to allow
                    # statements that can't run in a transaction block
                    self.conn.autocommit = True
                    self.ex(evolve[1])
                    self.conn.autocommit = False
                else:
                    for sql in evolve[1:]:
                        self.ex(sql)
            else:
                print('evolving', version, evolve.__doc__.strip(),
                      end='...')
                sys.stdout.flush()
                evolve()
            self.ex("update %s set version=%%s" % self.table, version)
            self.conn.commit()
            print("done")
            sys.stdout.flush()

class KarlEvolver(Evolver):

    table = 'karl_schema_version'

    def evolve0(self):
        """Add icontent_classes and can_view
        """
        self.ex("""
        CREATE TABLE if not exists icontent_classes(name text);
        insert into icontent_classes values %s;

        create or replace function can_view(
          state jsonb,
          principals text[])
          returns bool
        as $$
        declare
          acl jsonb;
          acli jsonb;
          parent_id bigint;
          want constant text[] := array['view', '::'];
        begin
          if state is null then return false; end if;
          acl := state -> '__acl__';
          if acl is not null then
            for i in 0 .. (jsonb_array_length(acl) - 1)
            loop
              acli := acl -> i;
              if acli ->> 1 = any(principals) and acli -> 2 ?| want then
                 return acli ->> 0 = 'Allow';
              end if;
            end loop;
          end if;
          parent_id := (state -> '__parent__' -> 'id' ->> 0)::bigint;
          if parent_id is null then return false; end if;
          select object_json.state from object_json where zoid = parent_id
          into state;
          return can_view(state, principals);
        end
        $$ language plpgsql immutable;
        """ % ', '.join(
                    "('karl.%s')" % name for name in (
                        'content.models.files.CommunityFolder',
                        'content.models.calendar.CalendarLayer',
                        'content.models.intranets.IntranetsFolder',
                        'content.models.commenting.Comment',
                        'content.models.calendar.CalendarCategory',
                        'models.community.Community',
                        'content.models.files.CommunityRootFolder',
                        'content.models.calendar.Calendar',
                        'content.models.files.CommunityFile',
                        'content.models.wiki.Wiki',
                        'content.models.page.Page',
                        'content.models.blog.Blog',
                        'content.models.forum.Forum',
                        'content.models.blog.BlogEntry',
                        'content.models.forum.ForumTopic',
                        'models.peopledirectory.PeopleDirectory',
                        'content.models.forum.ForumsFolder',
                        'content.models.wiki.WikiPage',
                        'models.profile.ProfilesFolder',
                        'models.community.CommunitiesFolder',
                        'content.models.calendar.CalendarEvent',
                        'models.profile.Profile',
                        'models.site.Site',
                        'content.models.blog.MailinTraceBlog',
                        'models.feedstorage.Feed',
                        'models.feedstorage.FeedsContainer',
                        'content.models.references.ReferenceSection',
                        'content.models.references.ReferenceManual',
                        'content.models.news.NewsItem',
                        'models.members.Invitation',
                        )
                    )
                )

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

    evolve1 = add_implemented_by

    def evolve2(self):
        """Add functions needed by indexes
        """
        import karl.models, os
        with open(os.path.join(os.path.dirname(karl.models.__file__),
                               'newtqbe.sql')) as f:
            self.ex(f.read().replace('%', '%%'))

    def evolve3(self):
        """Add the interfaces index
        """
        from karl.models.newtqbe import qbe
        self.ex1(*qbe.index_sql('interfaces'))

    def evolve4(self):
        """Add the creation_date index
        """
        from karl.models.newtqbe import qbe
        self.ex1(*qbe.index_sql('creation_date'))

    def evolve5(self):
        """Add the allowed index
        """
        from karl.models.newtqbe import qbe
        self.ex1(*qbe.index_sql('allowed'))

    def analyze(self):
        "analyze newt"
        self.ex("analyze newt")

    evolve6 = analyze
