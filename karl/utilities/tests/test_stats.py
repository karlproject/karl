import unittest

from zope.testing.cleanup import cleanUp

class TestCommunityStats(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _call_fut(self, context):
        from karl.utilities.stats import collect_community_stats as fut
        return fut(context)

    def _mk_dummy_site(self):
        import datetime
        from karl.content.interfaces import IBlogEntry
        from karl.content.interfaces import ICalendarEvent
        from karl.content.interfaces import ICommunityFile
        from karl.content.interfaces import IWikiPage
        from karl.models.interfaces import IComment
        from karl.testing import DummyCommunity
        from karl.testing import DummyModel
        from karl.testing import DummyRoot
        from repoze.workflow.testing import registerDummyWorkflow
        from repoze.workflow.testing import DummyWorkflow
        from zope.interface import directlyProvides

        site = DummyRoot()
        site.tags = DummyTags()
        communities = site['communities'] = DummyModel()

        big_endians = communities['big_endians'] = DummyCommunity()
        big_endians.title = 'Big Endians'
        big_endians.member_names = ['fred', 'martin', 'daniela']
        big_endians.moderator_names = ['fred', 'daniela']
        big_endians.created = datetime.datetime(2010, 5, 12, 2, 42)
        big_endians.creator = 'daniela'
        big_endians.content_modified = datetime.datetime(2010, 6, 12, 2, 42)

        content = big_endians['wiki1'] = DummyModel()
        content.created = datetime.datetime.now()
        content.creator = 'daniela'
        directlyProvides(content, IWikiPage)

        content = big_endians['wiki2'] = DummyModel()
        content.created = datetime.datetime(1975, 7, 7, 7, 23)
        content.creator = 'fred'
        directlyProvides(content, IWikiPage)

        little_endians = communities['little_endians'] = DummyCommunity()
        little_endians.title = 'Little Endians'
        little_endians.member_names = ['dusty', 'roberta', 'nina']
        little_endians.moderator_names = ['nina']
        little_endians.created = datetime.datetime(2010, 5, 13, 6, 23)
        little_endians.creator = 'nina'
        little_endians.content_modified = datetime.datetime(
            2010, 6, 12, 3, 42
        )

        content = little_endians['blog1'] = DummyModel()
        content.created = datetime.datetime.now()
        content.creator = 'nina'
        directlyProvides(content, IBlogEntry)

        content['comment1'] = DummyModel()
        content = content['comment1']
        content.created = datetime.datetime.now()
        content.creator = 'roberta'
        directlyProvides(content, IComment)

        content = little_endians['file1'] = DummyModel()
        content.created = datetime.datetime.now()
        content.creator = 'dusty'
        directlyProvides(content, ICommunityFile)

        content = little_endians['event1'] = DummyModel()
        content.created = datetime.datetime.now()
        content.creator = 'dusty'
        directlyProvides(content, ICalendarEvent)

        registerDummyWorkflow('security', DummyWorkflow())

        return site

    def test_it(self):
        import datetime
        report = list(self._call_fut(self._mk_dummy_site()))
        report.sort(key=lambda x: x['id'])
        self.assertEqual(len(report), 2)
        row = report.pop(0)
        self.assertEqual(row['community'], 'Big Endians')
        self.assertEqual(row['id'], 'big_endians')
        self.assertEqual(row['members'], 3)
        self.assertEqual(row['moderators'], 2)
        self.assertEqual(row['last_activity'], datetime.datetime(
            2010, 6, 12, 2, 42
        ))
        self.assertEqual(row['create_date'], datetime.datetime(
            2010, 5, 12, 2, 42
        ))
        self.assertEqual(row['wiki_pages'], 2)
        self.assertEqual(row['blog_entries'], 0)
        self.assertEqual(row['comments'], 0)
        self.assertEqual(row['files'], 0)
        self.assertEqual(row['calendar_events'], 0)
        self.assertEqual(row['community_tags'], 2)
        self.assertAlmostEqual(row['percent_engaged'], 33.33333333)

        row = report.pop(0)
        self.assertEqual(row['community'], 'Little Endians')
        self.assertEqual(row['id'], 'little_endians')
        self.assertEqual(row['members'], 3)
        self.assertEqual(row['moderators'], 1)
        self.assertEqual(row['last_activity'], datetime.datetime(
            2010, 6, 12, 3, 42
        ))
        self.assertEqual(row['create_date'], datetime.datetime(
            2010, 5, 13, 6, 23
        ))
        self.assertEqual(row['wiki_pages'], 0)
        self.assertEqual(row['blog_entries'], 1)
        self.assertEqual(row['comments'], 1)
        self.assertEqual(row['files'], 1)
        self.assertEqual(row['calendar_events'], 0)
        self.assertEqual(row['community_tags'], 1)
        self.assertAlmostEqual(row['percent_engaged'], 66.666666666)

class DummyTags(object):
    tags = {
        'big_endians': ['cute', 'clever'],
        'little_endians': ['crooners'],
    }

    def getTags(self, community=None):
        return self.tags.get(community, [])
