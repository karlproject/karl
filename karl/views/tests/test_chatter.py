import unittest

from pyramid import testing

from karl import testing as karltesting


class Test_recent_chatter_json(unittest.TestCase):

    def _callFUT(self, context, request):
        from karl.views.chatter import recent_chatter_json
        return recent_chatter_json(context, request)

    def test_empty_chatterbox(self):
        site = testing.DummyModel()
        site['chatter'] = context = _makeChatterbox()
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        self.assertEqual(info['recent'], [])
        self.failIf(context._tag or context._names or
                    context._community or context._creators)

    def test_filled_chatterbox(self):
        site = testing.DummyModel()
        quips = [DummyQuip('1'), DummyQuip('2'), DummyQuip('3')]
        site['chatter'] = context = _makeChatterbox(quips)
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        self.assertEqual(info['recent'], quips)

    def test_overfilled_chatterbox(self):
        site = testing.DummyModel()
        quips = []
        for i in range(30):
            quips.append(DummyQuip(str(i)))
        site['chatter'] = context = _makeChatterbox(quips)
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        self.assertEqual(info['recent'], quips[:20])

    def test_filled_chatterbox_w_start_and_count(self):
        site = testing.DummyModel()
        quips = []
        for i in range(30):
            quips.append(DummyQuip(str(i)))
        site['chatter'] = context = _makeChatterbox(quips)
        request = testing.DummyRequest(GET={'start': 2, 'count': 5})
        info = self._callFUT(context, request)
        self.assertEqual(info['recent'], quips[2:7])


class Test_recent_chatter(unittest.TestCase):

    def _callFUT(self, context, request):
        from karl.views.chatter import recent_chatter
        return recent_chatter(context, request)

    def test_empty_chatterbox(self):
        site = testing.DummyModel()
        site['chatter'] = context = _makeChatterbox()
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        self.assertEqual(info['api'].page_title, 'Recent Chatter')
        self.assertEqual(info['recent'], [])
        self.assertEqual(info['qurl'](context), 'http://example.com/chatter/')


class Test_creators_chatter_json(unittest.TestCase):

    def _callFUT(self, context, request):
        from karl.views.chatter import creators_chatter_json
        return creators_chatter_json(context, request)

    def test_wo_parm(self):
        site = testing.DummyModel()
        site['chatter'] = context = _makeChatterbox()
        request = testing.DummyRequest()
        self.assertRaises(KeyError, self._callFUT, context, request)

    def test_empty_chatterbox_creators_as_string(self):
        site = testing.DummyModel()
        site['chatter'] = context = _makeChatterbox()
        request = testing.DummyRequest(GET={'creators': 'USER'})
        info = self._callFUT(context, request)
        self.assertEqual(info['creators'], ['USER'])
        self.assertEqual(info['recent'], [])
        self.assertEqual(context._creators, ('USER',))
        self.failIf(context._names or context._tag or context._community)

    def test_filled_chatterbox_creators_as_tuple(self):
        site = testing.DummyModel()
        quips = [DummyQuip('1'), DummyQuip('2'), DummyQuip('3')]
        site['chatter'] = context = _makeChatterbox(quips)
        request = testing.DummyRequest(GET={'creators': ('USER',)})
        info = self._callFUT(context, request)
        self.assertEqual(info['creators'], ['USER'])
        self.assertEqual(info['recent'], quips)

    def test_overfilled_chatterbox(self):
        site = testing.DummyModel()
        quips = []
        for i in range(30):
            quips.append(DummyQuip(str(i)))
        site['chatter'] = context = _makeChatterbox(quips)
        request = testing.DummyRequest(GET={'creators': ['USER', 'USER2']})
        info = self._callFUT(context, request)
        self.assertEqual(info['creators'], ['USER', 'USER2'])
        self.assertEqual(info['recent'], quips[:20])
        self.assertEqual(context._creators, ('USER', 'USER2'))
        self.failIf(context._names or context._tag or context._community)

    def test_filled_chatterbox_w_start_and_count(self):
        site = testing.DummyModel()
        quips = []
        for i in range(30):
            quips.append(DummyQuip(str(i)))
        site['chatter'] = context = _makeChatterbox(quips)
        request = testing.DummyRequest(GET={'creators': ['USER', 'USER2'],
                                            'start': 2, 'count': 5})
        info = self._callFUT(context, request)
        self.assertEqual(info['recent'], quips[2:7])


class Test_creators_chatter(unittest.TestCase):

    def _callFUT(self, context, request):
        from karl.views.chatter import creators_chatter
        return creators_chatter(context, request)

    def test_wo_parm(self):
        site = testing.DummyModel()
        site['chatter'] = context = _makeChatterbox()
        request = testing.DummyRequest()
        found = self._callFUT(context, request)
        self.assertEqual(found.location, 'http://example.com/chatter/')

    def test_empty_chatterbox_creators_as_string(self):
        site = testing.DummyModel()
        site['chatter'] = context = _makeChatterbox()
        request = testing.DummyRequest(GET={'creators': 'USER'})
        info = self._callFUT(context, request)
        self.assertEqual(info['creators'], ['USER'])
        self.assertEqual(info['api'].page_title, 'Chatter: @USER')
        self.assertEqual(info['recent'], [])
        self.assertEqual(info['qurl'](context), 'http://example.com/chatter/')

    def test_empty_chatterbox_creators_as_list(self):
        site = testing.DummyModel()
        site['chatter'] = context = _makeChatterbox()
        request = testing.DummyRequest(GET={'creators': ['USER', 'USER2']})
        info = self._callFUT(context, request)
        self.assertEqual(info['creators'], ['USER', 'USER2'])
        self.assertEqual(info['api'].page_title, 'Chatter: @USER, @USER2')
        self.assertEqual(info['recent'], [])
        self.assertEqual(info['qurl'](context), 'http://example.com/chatter/')


class Test_names_chatter_json(unittest.TestCase):

    def _callFUT(self, context, request):
        from karl.views.chatter import names_chatter_json
        return names_chatter_json(context, request)

    def test_wo_parm(self):
        site = testing.DummyModel()
        site['chatter'] = context = _makeChatterbox()
        request = testing.DummyRequest()
        self.assertRaises(KeyError, self._callFUT, context, request)

    def test_empty_chatterbox_names_as_string(self):
        site = testing.DummyModel()
        site['chatter'] = context = _makeChatterbox()
        request = testing.DummyRequest(GET={'names': 'USER'})
        info = self._callFUT(context, request)
        self.assertEqual(info['names'], ['USER'])
        self.assertEqual(info['recent'], [])
        self.assertEqual(context._names, ('USER',))
        self.failIf(context._creators or context._tag or context._community)

    def test_filled_chatterbox_names_as_tuple(self):
        site = testing.DummyModel()
        quips = [DummyQuip('1'), DummyQuip('2'), DummyQuip('3')]
        site['chatter'] = context = _makeChatterbox(quips)
        request = testing.DummyRequest(GET={'names': ('USER',)})
        info = self._callFUT(context, request)
        self.assertEqual(info['names'], ['USER'])
        self.assertEqual(info['recent'], quips)
        self.assertEqual(context._names, ('USER',))

    def test_overfilled_chatterbox(self):
        site = testing.DummyModel()
        quips = []
        for i in range(30):
            quips.append(DummyQuip(str(i)))
        site['chatter'] = context = _makeChatterbox(quips)
        request = testing.DummyRequest(GET={'names': ['USER', 'USER2']})
        info = self._callFUT(context, request)
        self.assertEqual(info['names'], ['USER', 'USER2'])
        self.assertEqual(info['recent'], quips[:20])
        self.assertEqual(context._names, ('USER', 'USER2'))

    def test_filled_chatterbox_w_start_and_count(self):
        site = testing.DummyModel()
        quips = []
        for i in range(30):
            quips.append(DummyQuip(str(i)))
        site['chatter'] = context = _makeChatterbox(quips)
        request = testing.DummyRequest(GET={'names': ['USER', 'USER2'],
                                            'start': 2, 'count': 5})
        info = self._callFUT(context, request)
        self.assertEqual(info['recent'], quips[2:7])


class Test_names_chatter(unittest.TestCase):

    def _callFUT(self, context, request):
        from karl.views.chatter import names_chatter
        return names_chatter(context, request)

    def test_wo_parm(self):
        site = testing.DummyModel()
        site['chatter'] = context = _makeChatterbox()
        request = testing.DummyRequest()
        found = self._callFUT(context, request)
        self.assertEqual(found.location, 'http://example.com/chatter/')

    def test_empty_chatterbox_names_as_string(self):
        site = testing.DummyModel()
        site['chatter'] = context = _makeChatterbox()
        request = testing.DummyRequest(GET={'names': 'USER'})
        info = self._callFUT(context, request)
        self.assertEqual(info['names'], ['USER'])
        self.assertEqual(info['api'].page_title, 'Chatter: @USER')
        self.assertEqual(info['recent'], [])
        self.assertEqual(info['qurl'](context), 'http://example.com/chatter/')

    def test_empty_chatterbox_names_as_list(self):
        site = testing.DummyModel()
        site['chatter'] = context = _makeChatterbox()
        request = testing.DummyRequest(GET={'names': ['USER', 'USER2']})
        info = self._callFUT(context, request)
        self.assertEqual(info['names'], ['USER', 'USER2'])
        self.assertEqual(info['api'].page_title, 'Chatter: @USER, @USER2')
        self.assertEqual(info['recent'], [])
        self.assertEqual(info['qurl'](context), 'http://example.com/chatter/')


class Test_tag_chatter_json(unittest.TestCase):

    def _callFUT(self, context, request):
        from karl.views.chatter import tag_chatter_json
        return tag_chatter_json(context, request)

    def test_wo_parm(self):
        site = testing.DummyModel()
        site['chatter'] = context = _makeChatterbox()
        request = testing.DummyRequest()
        self.assertRaises(KeyError, self._callFUT, context, request)

    def test_empty_chatterbox(self):
        site = testing.DummyModel()
        site['chatter'] = context = _makeChatterbox()
        request = testing.DummyRequest(GET={'tag': 'sometag'})
        info = self._callFUT(context, request)
        self.assertEqual(info['tag'], 'sometag')
        self.assertEqual(info['recent'], [])
        self.assertEqual(context._tag, 'sometag')
        self.failIf(context._names or context._community or context._creators)

    def test_filled_chatterbox(self):
        site = testing.DummyModel()
        quips = [DummyQuip('1'), DummyQuip('2'), DummyQuip('3')]
        site['chatter'] = context = _makeChatterbox(quips)
        request = testing.DummyRequest(GET={'tag': 'sometag'})
        info = self._callFUT(context, request)
        self.assertEqual(info['recent'], quips)

    def test_overfilled_chatterbox(self):
        site = testing.DummyModel()
        quips = []
        for i in range(30):
            quips.append(DummyQuip(str(i)))
        site['chatter'] = context = _makeChatterbox(quips)
        request = testing.DummyRequest(GET={'tag': 'sometag'})
        info = self._callFUT(context, request)
        self.assertEqual(info['recent'], quips[:20])

    def test_filled_chatterbox_w_start_and_count(self):
        site = testing.DummyModel()
        quips = []
        for i in range(30):
            quips.append(DummyQuip(str(i)))
        site['chatter'] = context = _makeChatterbox(quips)
        request = testing.DummyRequest(GET={'tag': 'sometag',
                                            'start': 2, 'count': 5})
        info = self._callFUT(context, request)
        self.assertEqual(info['recent'], quips[2:7])


class Test_tag_chatter(unittest.TestCase):

    def _callFUT(self, context, request):
        from karl.views.chatter import tag_chatter
        return tag_chatter(context, request)

    def test_wo_parm(self):
        site = testing.DummyModel()
        site['chatter'] = context = _makeChatterbox()
        request = testing.DummyRequest()
        found = self._callFUT(context, request)
        self.assertEqual(found.location, 'http://example.com/chatter/')

    def test_empty_chatterbox(self):
        site = testing.DummyModel()
        site['chatter'] = context = _makeChatterbox()
        request = testing.DummyRequest(GET={'tag': 'sometag'})
        info = self._callFUT(context, request)
        self.assertEqual(info['api'].page_title, 'Chatter: #sometag')
        self.assertEqual(info['recent'], [])
        self.assertEqual(info['qurl'](context), 'http://example.com/chatter/')


class Test_community_chatter_json(unittest.TestCase):

    def _callFUT(self, context, request):
        from karl.views.chatter import community_chatter_json
        return community_chatter_json(context, request)

    def test_empty_chatterbox(self):
        site = testing.DummyModel()
        site['chatter'] = cb = _makeChatterbox()
        site['communities'] = cf = testing.DummyModel()
        cf['testing'] = context = testing.DummyModel()
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        self.assertEqual(info['community'], 'testing')
        self.assertEqual(info['recent'], [])
        self.assertEqual(cb._community, 'testing')
        self.failIf(cb._names or cb._creators or cb._tag)

    def test_filled_chatterbox(self):
        site = testing.DummyModel()
        quips = [DummyQuip('1'), DummyQuip('2'), DummyQuip('3')]
        site['chatter'] = cb = _makeChatterbox(quips)
        site['communities'] = cf = testing.DummyModel()
        cf['testing'] = context = testing.DummyModel()
        site['communities'] = cf = testing.DummyModel()
        cf['testing'] = context = testing.DummyModel()
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        self.assertEqual(info['recent'], quips)

    def test_overfilled_chatterbox(self):
        site = testing.DummyModel()
        quips = []
        for i in range(30):
            quips.append(DummyQuip(str(i)))
        site['chatter'] = cb = _makeChatterbox(quips)
        site['communities'] = cf = testing.DummyModel()
        cf['testing'] = context = testing.DummyModel()
        site['communities'] = cf = testing.DummyModel()
        cf['testing'] = context = testing.DummyModel()
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        self.assertEqual(info['recent'], quips[:20])

    def test_filled_chatterbox_w_start_and_count(self):
        site = testing.DummyModel()
        quips = []
        for i in range(30):
            quips.append(DummyQuip(str(i)))
        site['chatter'] = cb = _makeChatterbox(quips)
        site['communities'] = cf = testing.DummyModel()
        cf['testing'] = context = testing.DummyModel()
        site['communities'] = cf = testing.DummyModel()
        cf['testing'] = context = testing.DummyModel()
        request = testing.DummyRequest(GET={'start': 2, 'count': 5})
        info = self._callFUT(context, request)
        self.assertEqual(info['recent'], quips[2:7])


class Test_community_chatter(unittest.TestCase):

    def _callFUT(self, context, request):
        from karl.views.chatter import community_chatter
        return community_chatter(context, request)

    def test_empty_chatterbox(self):
        site = testing.DummyModel()
        site['chatter'] = cb = _makeChatterbox()
        site['communities'] = cf = testing.DummyModel()
        cf['testing'] = context = testing.DummyModel()
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        self.assertEqual(info['api'].page_title, 'Chatter: &testing')
        self.assertEqual(info['recent'], [])
        self.assertEqual(info['qurl'](context),
                         'http://example.com/communities/testing/')


class Test_add_chatter(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        from karl.views.chatter import add_chatter
        return add_chatter(context, request)

    def test_it(self):
        _registerSecurityPolicy('user')
        site = testing.DummyModel()
        site['chatter'] = context = _makeChatterbox()
        request = testing.DummyRequest()
        request.POST['text'] = 'This is a quip.'
        found = self._callFUT(context, request)
        self.assertEqual(found.location, 'http://example.com/chatter/')
        self.assertEqual(context._added.text, 'This is a quip.')
        self.assertEqual(context._added.creator, 'user')


def _makeChatterbox(recent=()):

    class _Chatterbox(testing.DummyModel):
        _names = _tag = _community = _added = _creators = None
        def __init__(self, recent):
            self._recent = recent
        def addQuip(self, text, creator):
            self._added = testing.DummyModel(text=text, creator=creator)
        def recent(self):
            return self._recent
        def recentWithCreators(self, *creators):
            self._creators = creators
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


def _registerSecurityPolicy(userid):
    karltesting.registerDummySecurityPolicy(userid)


class DummyQuip(object):
    def __init__(self, text='Dummy', creator='USER'):
        self.text = text
        self.creator = creator
    def __repr__(self):
        return '%s: %s, %s' % (self.__class__.__name__, self.text, self.creator)

class DummySecurityPolicy:
    """ A standin for both an IAuthentication and IAuthorization policy """
    def __init__(self, userid=None, groupids=(), permissions=None):
        self.userid = userid

    def authenticated_userid(self, request):
        return self.userid
