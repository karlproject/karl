import unittest

from pyramid import testing

from karl import testing as karltesting


def _makeChatterbox(recent=()):

    class _Chatterbox(testing.DummyModel):
        _names = _tag = _community = _added = None
        def __init__(self, recent):
            self._recent = recent
        def addQuip(self, text, creator):
            self._added = testing.DummyModel(text=text, creator=creator)
        def recent(self):
            return self._recent
        def recentWithNames(self, *names):
            self._names = names
            return self._recent
        def recentWithTag(self, tag):
            self._tag = tag
            return self._recent
        def recentWithCommunity(self, community):
            self._community = community
            return self._recent

    return _Chatterbox(recent)


class RecentChatterViewTests(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        from karl.views.chatter import recent_chatter
        return recent_chatter(context, request)

    def test_empty_chatterbox(self):
        context = testing.DummyModel()
        context['chatter'] = _makeChatterbox()
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        self.assertEqual(info['api'].page_title, 'Recent Chatter')
        self.assertEqual(list(info['recent']), [])
        self.assertEqual(info['qurl'](context), 'http://example.com/')

    def test_filled_chatterbox(self):
        context = testing.DummyModel()
        quip1, quip2, quip3 = object(), object(), object()
        context['chatter'] = _makeChatterbox((quip3, quip2, quip1))
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        self.assertEqual(list(info['recent']), [quip3, quip2, quip1])

    def test_overfilled_chatterbox(self):
        context = testing.DummyModel()
        context['chatter'] = _makeChatterbox([object()] * 30)
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        self.assertEqual(len(list(info['recent'])), 20)
