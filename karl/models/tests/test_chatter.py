import unittest

class ChatterboxTests(unittest.TestCase):

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


class QuipTests(unittest.TestCase):

    def _getTargetClass(self):
        from karl.models.chatter import Quip
        return Quip

    def _makeOne(self, text=''):
        return self._getTargetClass()(text)

    def test_class_conforms_to_IQuip(self):
        from zope.interface.verify import verifyClass
        from karl.models.interfaces import IQuip
        verifyClass(IQuip, self._getTargetClass())

    def test_instance_conforms_to_IQuip(self):
        from zope.interface.verify import verifyObject
        from karl.models.interfaces import IQuip
        verifyObject(IQuip, self._makeOne())

    def test_empty(self):
        quip = self._makeOne()
        self.assertEqual(quip.text, '')
        self.assertEqual(list(quip.names), [])
        self.assertEqual(list(quip.tags), [])
        self.assertEqual(list(quip.communities), [])

    def test_text_immutable(self):
        quip = self._makeOne('before')
        def _set_text():
            quip.text = 'after'
        self.assertRaises(AttributeError, _set_text)
        self.assertEqual(quip.text, 'before')

    def test_wo_syntax(self):
        quip = self._makeOne('This is a test')
        self.assertEqual(quip.text, 'This is a test')
        self.assertEqual(list(quip.names), [])
        self.assertEqual(list(quip.tags), [])
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
