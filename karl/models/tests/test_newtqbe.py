# Some minimal tests of qbe queries to check sql generation
import mock
from newt.db import connection
from newt.db.tests.base import TestCase

class QBETests(TestCase):

    def setUp(self):
        TestCase.setUp(self)
        self.conn = connection(self.dsn)
        self.root = self.conn.root()

    def tearDown(self):
        self.conn.close()
        TestCase.tearDown(self)

    @mock.patch("newt.db.search.search")
    def test_people_show_profile_view(self, search):
        from repoze.lemonade.interfaces import IContent
        from ..newtqbe import SQLCatalogSearch

        catalog_search = SQLCatalogSearch(self.root)
        search.return_value = ()
        self.assertEqual(
            (0, ()),
            catalog_search(
                sort_index='creation_date', reverse=True,
                interfaces=[IContent], limit=5, creator='foo',
                can_view={'query': ['foo', 'bar'], 'operator': 'or'},
                want_count=False,
                )[:2])
        self.assertEqual(
            norm('''
            select *
            from newt
            where state ? '__parent__' AND state ? '__name__' AND
                  newt_can_view(state, ARRAY['foo', 'bar']) AND
                  (state @> '{"creator": "foo"}'::jsonb) AND
                  interfaces(class_name) &&
                    ARRAY['repoze.lemonade.interfaces.IContent']
            ORDER BY (state ->> 'created') DESC limit 5
            '''),
            norm(search.call_args[0][1]))

    @mock.patch("newt.db.search.search_batch")
    def test_people_recent_content_view(self, search_batch):
        from repoze.lemonade.interfaces import IContent
        from ..newtqbe import SQLCatalogSearch

        catalog_search = SQLCatalogSearch(self.root)
        search_batch.return_value = (0, ())
        self.assertEqual(
            (0, ()),
            catalog_search(
                sort_index='creation_date', reverse=True,
                interfaces=[IContent], limit=5, creator='foo',
                can_view={'query': ['foo', 'bar'], 'operator': 'or'},
                )[:2])
        self.assertEqual(
            norm('''
            select *
            from newt
            where state ? '__parent__' AND state ? '__name__' AND
                  newt_can_view(state, ARRAY['foo', 'bar']) AND
                  (state @> '{"creator": "foo"}'::jsonb) AND
                  interfaces(class_name) &&
                    ARRAY['repoze.lemonade.interfaces.IContent']
            ORDER BY (state ->> 'created') DESC
            '''),
            norm(search_batch.call_args[0][1]))
        self.assertEqual((0, 5), search_batch.call_args[0][2:])

    @mock.patch("newt.db.search.search_batch")
    def test_community_get_recent_items_batch(self, search_batch):
        from ..newtqbe import SQLCatalogSearch
        from ..interfaces import ICommunityContent
        catalog_search = SQLCatalogSearch(self.root)
        search_batch.return_value = (0, ())
        self.assertEqual(
            (0, ()),
            catalog_search(
                sort_index='modified_date', reverse=True,
                interfaces=[ICommunityContent], limit=10,
                community=self.root,
                can_view={'query': ['foo', 'bar'], 'operator': 'or'},
                )[:2])
        self.assertEqual(
            norm('''
            select *
            from newt natural join karlex
            where newt_can_view(state, ARRAY['foo', 'bar']) AND
                  ((karlex.community_zoid) = 0) AND
                  interfaces(class_name) &&
                    ARRAY['karl.models.interfaces.ICommunityContent']
            ORDER BY (state ->> 'modified') DESC
            '''),
            norm(search_batch.call_args[0][1]))
        self.assertEqual((0, 10), search_batch.call_args[0][2:])

def norm(text):
    return ' '.join(text.strip().split())
