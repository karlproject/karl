import unittest

from pyramid import testing

import karl.testing

class TestTempFolder(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _target_class(self):
        from karl.models.tempfolder import TempFolder
        return TempFolder

    def _make_one(self):
        return self._target_class()()

    def test_class_implements_interface(self):
        from zope.interface.verify import verifyClass
        from karl.models.interfaces import ITempFolder
        self.failUnless(verifyClass(ITempFolder, self._target_class()))

    def test_object_provides_interface(self):
        from zope.interface.verify import verifyObject
        from karl.models.interfaces import ITempFolder
        self.failUnless(verifyObject(ITempFolder, self._make_one()))

    def test_ctor(self):
        import datetime
        from pyramid.authorization import Allow
        from pyramid.authorization import Everyone
        obj = self._make_one()
        self.assertEqual(obj.__acl__, [(Allow, Everyone, ('view',))])
        self.assertEqual(obj.LIFESPAN, datetime.timedelta(hours=24))
        self.assertEqual(obj.title, 'Temporary Folder')

    def test_add_document(self):
        obj = self._make_one()
        doc = testing.DummyModel(title='Foo')
        self.assertEqual(len(obj), 0)
        obj.add_document(doc)
        self.assertEqual(len(obj), 1)
        self.assertEqual(list(obj.values()), [doc,])

    def test_cleanup(self):
        import datetime
        obj = self._make_one()
        now = datetime.datetime.now()
        obj['one'] = testing.DummyModel(
            modified=now-datetime.timedelta(minutes=5)
        )
        obj['two'] = testing.DummyModel(
            modified=now-datetime.timedelta(hours=48)
        )
        self.failUnless('one' in obj)
        self.failUnless('two' in obj)
        obj.cleanup()
        self.failUnless('one' in obj)
        self.failIf('two' in obj)

    def test___setitem___emits_no_events(self):
        events = karl.testing.registerEventListener()
        del events[:]
        obj = self._make_one()
        obj['foo'] = testing.DummyModel()
        self.failIf(events)

    def test___delitem___emits_no_events(self):
        obj = self._make_one()
        obj['foo'] = testing.DummyModel()
        events = karl.testing.registerEventListener()
        del events[:]
        del obj['foo']
        self.failIf(events)
