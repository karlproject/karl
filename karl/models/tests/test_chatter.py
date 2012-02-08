import unittest

class _NowSetter(unittest.TestCase):
    _old_NOW = None

    def setUp(self):
        self._set_NOW(None)

    def tearDown(self):
        if self._old_NOW is not None:
            self._set_NOW(self._old_NOW)

    def _set_NOW(self, when):
        from karl.models import subscribers
        subscribers._NOW, self._old_NOW = when, subscribers._NOW

class ChatterboxTests(_NowSetter):

    def _getTargetClass(self):
        from karl.models.chatter import Chatterbox
        return Chatterbox

    def _makeOne(self):
        return self._getTargetClass()()

    def test_class_conforms_to_IChatterbox(self):
        from zope.interface.verify import verifyClass
        from karl.models.interfaces import IChatterbox
        verifyClass(IChatterbox, self._getTargetClass())

    def test_instance_conforms_to_IChatterbox(self):
        from zope.interface.verify import verifyObject
        from karl.models.interfaces import IChatterbox
        verifyObject(IChatterbox, self._makeOne())


class QuipTests(_NowSetter):
    _creator = 'TESTUSER'

    def _getTargetClass(self):
        from karl.models.chatter import Quip
        return Quip

    def _makeOne(self, text='', creator=None):
        if creator is None:
            creator = self._creator
        return self._getTargetClass()(text, creator)

    def test_class_conforms_to_IQuip(self):
        from zope.interface.verify import verifyClass
        from karl.models.interfaces import IQuip
        verifyClass(IQuip, self._getTargetClass())

    def test_instance_conforms_to_IQuip(self):
        from zope.interface.verify import verifyObject
        from karl.models.interfaces import IQuip
        verifyObject(IQuip, self._makeOne())

    def test_empty(self):
        NOW = object()
        self._set_NOW(NOW)
        quip = self._makeOne()
        self.assertEqual(quip.text, '')
        self.assertEqual(list(quip.names), [])
        self.assertEqual(list(quip.tags), [])
        self.assertEqual(list(quip.communities), [])
        self.assertEqual(quip.creator, self._creator)
        self.assertEqual(quip.modified_by, self._creator)
        self.failUnless(quip.created is NOW)
        self.failUnless(quip.modified is NOW)

    def test_wo_syntax(self):
        quip = self._makeOne('This is a test')
        self.assertEqual(quip.text, 'This is a test')
        self.assertEqual(list(quip.names), [])
        self.assertEqual(list(quip.tags), [])
        self.assertEqual(list(quip.communities), [])

    def test_text_immutable(self):
        quip = self._makeOne('before')
        def _set_text():
            quip.text = 'after'
        self.assertRaises(AttributeError, _set_text)
        self.assertEqual(quip.text, 'before')

    def test_names_immutable(self):
        quip = self._makeOne()
        def _set_names():
            quip.names = ['after', 'the', 'fact']
        self.assertRaises(AttributeError, _set_names)
        self.assertEqual(list(quip.names), [])

    def test_tags_immutable(self):
        quip = self._makeOne()
        def _set_tags():
            quip.tags = ['after', 'the', 'fact']
        self.assertRaises(AttributeError, _set_tags)
        self.assertEqual(list(quip.tags), [])

    def test_communities_immutable(self):
        quip = self._makeOne()
        def _set_communities():
            quip.communities = ['after', 'the', 'fact']
        self.assertRaises(AttributeError, _set_communities)
        self.assertEqual(list(quip.communities), [])

    def test_w_syntax(self):
        quip = self._makeOne('This is a test @name #tag &community')
        self.assertEqual(quip.text, 'This is a test @name #tag &community')
        self.assertEqual(list(quip.names), ['name'])
        self.assertEqual(list(quip.tags), ['tag'])
        self.assertEqual(list(quip.communities), ['community'])

    def test_multiple_names(self):
        quip = self._makeOne('@foo @bar @baz')
        self.assertEqual(quip.text, '@foo @bar @baz')
        self.assertEqual(sorted(quip.names), ['bar', 'baz', 'foo'])
        self.assertEqual(list(quip.tags), [])
        self.assertEqual(list(quip.communities), [])

    def test_multiple_tags(self):
        quip = self._makeOne('#foo #bar #baz')
        self.assertEqual(quip.text, '#foo #bar #baz')
        self.assertEqual(list(quip.names), [])
        self.assertEqual(sorted(quip.tags), ['bar', 'baz', 'foo'])
        self.assertEqual(list(quip.communities), [])

    def test_multiple_communities(self):
        quip = self._makeOne('&foo &bar &baz')
        self.assertEqual(quip.text, '&foo &bar &baz')
        self.assertEqual(list(quip.names), [])
        self.assertEqual(list(quip.tags), [])
        self.assertEqual(sorted(quip.communities), ['bar', 'baz', 'foo'])
