import unittest

class _NowSetter(unittest.TestCase):
    _old_NOW = None

    def setUp(self):
        self._set_NOW(None)

    def tearDown(self):
        if self._old_NOW is not None:
            self._set_NOW(self._old_NOW)

    def _set_NOW(self, when):
        from karl.models import chatter
        chatter._NOW, self._old_NOW = when, chatter._NOW

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

    def test_empty(self):
        cb = self._makeOne()
        self.assertEqual(len(cb), 0)
        self.assertEqual(list(cb), [])

    def test___getitem___miss(self):
        cb = self._makeOne()
        self.assertRaises(KeyError, cb.__getitem__, 'nonesuch')

    def test_addQuip(self):
        cb = self._makeOne()
        name = cb.addQuip('TEXT', 'USER')
        self.assertEqual(len(cb), 1)
        self.assertEqual(list(cb), [name])
        quip = cb[name]
        self.assertEqual(quip.text, 'TEXT')
        self.assertEqual(quip.creator, 'USER')
        self.assertEqual(list(cb.recent()), [quip])
        self.failUnless(quip.__parent__ is cb)
        self.assertEqual(quip.__name__, name)

    def test_addQuip_with_pruning(self):
        from appendonly import AppendStack
        cb = self._makeOne()
        # replace the stack with one which overflows quickly.
        cb._recent = AppendStack(1, 1)
        name1 = cb.addQuip('TEXT1', 'USER1')
        name2 = cb.addQuip('TEXT2', 'USER2')
        name3 = cb.addQuip('TEXT3', 'USER3')
        self.assertEqual(len(cb), 3)
        self.assertEqual(sorted(cb), sorted([name3, name2, name1]))
        # Overflowed twice
        self.assertEqual(cb._archive._generation, 1)

    def test_listFollowed_miss(self):
        cb = self._makeOne()
        self.assertEqual(list(cb.listFollowed('nonesuch')), [])

    def test_setFollowed(self):
        FOLLOWED = ['USER1', 'USER2', 'USER3']
        cb = self._makeOne()
        cb.setFollowed('USER', FOLLOWED)
        self.assertEqual(list(cb.listFollowed('USER')), FOLLOWED)

    def test_recent_with_multiple(self):
        cb = self._makeOne()
        name1 = cb.addQuip('TEXT1', 'USER')
        quip1 = cb[name1]
        name2 = cb.addQuip('TEXT2', 'USER2')
        quip2 = cb[name2]
        self.assertEqual(list(cb.recent()), [quip2, quip1])

    def test_recentFollowed_skips_names(self):
        FOLLOWED = ['USER1', 'USER2']
        cb = self._makeOne()
        cb.setFollowed('USER', FOLLOWED)
        name1 = cb.addQuip('TEXT1 @USER1', 'USER')
        quip1 = cb[name1]
        name2 = cb.addQuip('TEXT2', 'USER2')
        quip2 = cb[name2]
        name3 = cb.addQuip('TEXT3 @USER1', 'USER3')
        quip3 = cb[name3]
        self.assertEqual(list(cb.recentFollowed('USER')),
                         [quip2, quip1])

    def test_recentWithTag(self):
        cb = self._makeOne()
        name1 = cb.addQuip('TEXT1 #tag', 'USER')
        quip1 = cb[name1]
        name2 = cb.addQuip('TEXT2', 'USER2')
        quip2 = cb[name2]
        name3 = cb.addQuip('TEXT3 #tag', 'USER3')
        quip3 = cb[name3]
        self.assertEqual(list(cb.recentWithTag('tag')), [quip3, quip1])

    def test_recentWithCommunity(self):
        cb = self._makeOne()
        name1 = cb.addQuip('TEXT1 &community', 'USER')
        quip1 = cb[name1]
        name2 = cb.addQuip('TEXT2', 'USER2')
        quip2 = cb[name2]
        name3 = cb.addQuip('TEXT3 &community', 'USER3')
        quip3 = cb[name3]
        self.assertEqual(list(cb.recentWithCommunity('community')),
                         [quip3, quip1])

    def test_recentWithCreators_single(self):
        cb = self._makeOne()
        name1 = cb.addQuip('TEXT1 @name', 'USER')
        quip1 = cb[name1]
        name2 = cb.addQuip('TEXT2', 'USER2')
        quip2 = cb[name2]
        name3 = cb.addQuip('TEXT3 @name', 'USER3')
        quip3 = cb[name3]
        self.assertEqual(list(cb.recentWithCreators('USER')),
                         [quip1])
        self.assertEqual(list(cb.recentWithCreators('USER2')),
                         [quip2])
        self.assertEqual(list(cb.recentWithCreators('USER3')),
                         [quip3])

    def test_recentWithCreators_multiple(self):
        cb = self._makeOne()
        name1 = cb.addQuip('TEXT1 @name', 'USER')
        quip1 = cb[name1]
        name2 = cb.addQuip('TEXT2', 'USER2')
        quip2 = cb[name2]
        name3 = cb.addQuip('TEXT3 @name', 'USER3')
        quip3 = cb[name3]
        self.assertEqual(list(cb.recentWithCreators('USER', 'USER2')),
                         [quip2, quip1])
        self.assertEqual(list(cb.recentWithCreators('USER', 'USER3')),
                         [quip3, quip1])
        self.assertEqual(list(cb.recentWithCreators('USER2', 'USER3')),
                         [quip3, quip2])
        self.assertEqual(list(cb.recentWithCreators('USER', 'USER2', 'USER3')),
                         [quip3, quip2, quip1])

    def test_recentWithNames_excludes_creator(self):
        cb = self._makeOne()
        name1 = cb.addQuip('TEXT1 @name', 'USER')
        quip1 = cb[name1]
        name2 = cb.addQuip('TEXT2', 'USER2')
        quip2 = cb[name2]
        name3 = cb.addQuip('TEXT3 @name', 'USER3')
        quip3 = cb[name3]
        self.assertEqual(list(cb.recentWithNames('USER')),
                         [])
        self.assertEqual(list(cb.recentWithNames('USER2')),
                         [])
        self.assertEqual(list(cb.recentWithNames('USER3')),
                         [])

    def test_recentWithNames_single(self):
        cb = self._makeOne()
        name1 = cb.addQuip('TEXT1 @name', 'USER')
        quip1 = cb[name1]
        name2 = cb.addQuip('TEXT2', 'USER2')
        quip2 = cb[name2]
        name3 = cb.addQuip('TEXT3 @name', 'USER3')
        quip3 = cb[name3]
        self.assertEqual(list(cb.recentWithNames('name')),
                         [quip3, quip1])

    def test_recentWithNames_multiple(self):
        cb = self._makeOne()
        name1 = cb.addQuip('TEXT1 @name1', 'USER')
        quip1 = cb[name1]
        name2 = cb.addQuip('TEXT2', 'USER2')
        quip2 = cb[name2]
        name3 = cb.addQuip('TEXT3 @name2', 'USER3')
        quip3 = cb[name3]
        self.assertEqual(list(cb.recentWithNames('name1', 'name2')),
                         [quip3, quip1])


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
        def _add_names():
            quip.names += set(['after', 'the', 'fact'])
        self.assertRaises(TypeError, _add_names)
        self.assertEqual(list(quip.names), [])

    def test_tags_immutable(self):
        quip = self._makeOne()
        def _set_tags():
            quip.tags = ['after', 'the', 'fact']
        self.assertRaises(AttributeError, _set_tags)
        self.assertEqual(list(quip.tags), [])
        def _add_tags():
            quip.tags += set(['after', 'the', 'fact'])
        self.assertRaises(TypeError, _add_tags)
        self.assertEqual(list(quip.tags), [])

    def test_communities_immutable(self):
        quip = self._makeOne()
        def _set_communities():
            quip.communities = ['after', 'the', 'fact']
        self.assertRaises(AttributeError, _set_communities)
        self.assertEqual(list(quip.communities), [])
        def _add_communities():
            quip.communities += set(['after', 'the', 'fact'])
        self.assertRaises(TypeError, _add_communities)
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
