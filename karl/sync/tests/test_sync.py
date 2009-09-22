import unittest
import datetime

from zope.testing.cleanup import cleanUp
from zope.interface import implements
from zope.interface import Interface

from karl.sync.interfaces import IContentSource
from karl.sync.interfaces import IContentItem

class SyncTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

        from repoze.bfg.testing import DummyModel
        self.context = DummyModel()

        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(DummyContent, IDummyContent)

    def tearDown(self):
        cleanUp()

    def _make_one(self, source):
        from karl.sync.sync import Synchronizer
        return Synchronizer(source, self.context)

    def test_sync_empty_folder(self):
        import datetime
        from pytz import FixedOffset
        date1 = datetime.datetime(2009, 9, 22, 10, 9, 00,
                                  tzinfo=FixedOffset(-300))
        date2 = datetime.datetime(2009, 9, 22, 22, 9, 00,
                                  tzinfo=FixedOffset(-300))
        item1 = DummyItem(
            id='1234',
            name='foo',
            type=IDummyContent,
            workflow_state=None,
            created=date1,
            created_by='chris',
            modified=date2,
            modified_by='chris',
            children=[],
            deleted_children=[],
            attributes=dict(
                a='a',
                b=2,
                c=True,
                ),
            )

        item2 = DummyItem(
            id='5678',
            name='bar',
            type=IDummyContent,
            workflow_state=None,
            created=date2,
            created_by='paul',
            modified=date2,
            modified_by='paul',
            children=[],
            deleted_children=[],
            attributes=dict(
                a='z',
                b=9,
                c=False,
                ),
            )

        source = DummySource(
            items=[item1, item2],
            incremental=False,
            deleted_items=[]
            )

        self._make_one(source)()

        context = self.context
        self.assertEqual(len(self.context), 2)
        o = self.context['foo']
        self.assertEqual(o.__name__, 'foo')
        self.assertEqual(o.created, date1)
        self.assertEqual(o.created_by, 'chris')
        self.assertEqual(o.modified, date2)
        self.assertEqual(o.modified_by, 'chris')
        self.assertEqual(o.a, 'a')
        self.assertEqual(o.b, 2)
        self.assertEqual(o.c, True)

        o = self.context['bar']
        self.assertEqual(o.__name__, 'bar')
        self.assertEqual(o.created, date2)
        self.assertEqual(o.created_by, 'paul')
        self.assertEqual(o.modified, date2)
        self.assertEqual(o.modified_by, 'paul')
        self.assertEqual(o.a, 'z')
        self.assertEqual(o.b, 9)
        self.assertEqual(o.c, False)

class DummySource(object):
    implements(IContentSource)

    def __init__(self, **kw):
        for k,v in kw.items():
            setattr(self, k, v)

class DummyItem(object):
    implements(IContentItem)

    def __init__(self, **kw):
        for k,v in kw.items():
            setattr(self, k, v)

class IDummyContent(Interface):
    pass

class DummyContent(object):
    implements(IDummyContent)
