import unittest

from pyramid import testing

from karl import testing as karltesting


class Test_quip_info(unittest.TestCase):

    def _callFUT(self, request, *quips):
        from karl.views.chatter import quip_info
        return quip_info(request, *quips)

    def test_single(self):
        request = testing.DummyRequest()
        quip = DummyQuip()
        infos = self._callFUT(request, quip)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info['text'], quip.text)
        self.assertEqual(info['creator'], quip.creator)
        self.assertEqual(info['timeago'], '2012-02-23T20:29:47Z') # XXX zone?
        self.assertEqual(info['names'], [])
        self.assertEqual(info['communities'], [])
        self.assertEqual(info['tags'], [])
        self.assertEqual(info['url'], 'http://example.com/')

    def test_multiple(self):
        request = testing.DummyRequest()
        quips = DummyQuip('1'), DummyQuip('2')
        infos = self._callFUT(request, *quips)
        self.assertEqual(len(infos), len(quips))
        for info, quip in zip(infos, quips):
            self.assertEqual(info['text'], quip.text)
            self.assertEqual(info['creator'], quip.creator)
            self.assertEqual(info['timeago'], '2012-02-23T20:29:47Z')# XXX zone?
            self.assertEqual(info['names'], [])
            self.assertEqual(info['communities'], [])
            self.assertEqual(info['tags'], [])
            self.assertEqual(info['url'], 'http://example.com/')


def _verify_quips(infos, quips, request):
    from karl.views.chatter import quip_info
    assert len(infos) == len(quips)
    for found, expected in zip(infos, quip_info(request, *quips)):
        assert found == expected


class Test_all_chatter_json(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        from karl.views.chatter import all_chatter_json
        return all_chatter_json(context, request)

    def test_empty_chatterbox(self):
        _registerSecurityPolicy('user')
        site = testing.DummyModel()
        site['chatter'] = context = _makeChatterbox()
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        self.assertEqual(info['recent'], [])
        self.failIf(context._followed or context._tag or context._names or
                    context._community or context._creators)

    def test_filled_chatterbox(self):
        _registerSecurityPolicy('user')
        site = testing.DummyModel()
        quips = [DummyQuip('1'), DummyQuip('2'), DummyQuip('3')]
        site['chatter'] = context = _makeChatterbox(quips)
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        _verify_quips(info['recent'], quips, request)

    def test_filled_chatterbox_skips_unauthorized_private_quips(self):
        _registerSecurityPolicy('user', permissive=False)
        site = testing.DummyModel()
        quips = [DummyQuip('1'), DummyQuip('2'), DummyQuip('3')]
        site['chatter'] = context = _makeChatterbox(quips)
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        self.assertEqual(info['recent'], [])

    def test_overfilled_chatterbox(self):
        _registerSecurityPolicy('user')
        site = testing.DummyModel()
        quips = []
        for i in range(30):
            quips.append(DummyQuip(str(i)))
        site['chatter'] = context = _makeChatterbox(quips)
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        _verify_quips(info['recent'], quips[:20], request)

    def test_filled_chatterbox_w_start_and_count(self):
        _registerSecurityPolicy('user')
        site = testing.DummyModel()
        quips = []
        for i in range(30):
            quips.append(DummyQuip(str(i)))
        site['chatter'] = context = _makeChatterbox(quips)
        request = testing.DummyRequest(GET={'start': 2, 'count': 5})
        info = self._callFUT(context, request)
        _verify_quips(info['recent'], quips[2:7], request)

    def test_filled_chatterbox_w_since_and_count(self):
        from datetime import datetime
        from datetime import timedelta
        from karl.views.chatter import TIMEAGO_FORMAT
        now = datetime.utcnow()
        _registerSecurityPolicy('user')
        site = testing.DummyModel()
        quips = []
        for i in range(30):
            # from 15 sec ago to 14 sec in the future
            when = now + timedelta(0, i - 15)
            quips.append(DummyQuip(str(i), created=when))
        quips.reverse() # get them in recency-order
        site['chatter'] = context = _makeChatterbox(quips)
        request = testing.DummyRequest(
                    GET={'since': now.strftime(TIMEAGO_FORMAT), 'count': 5})
        info = self._callFUT(context, request)
        _verify_quips(info['recent'], quips[10:15], request)

    def test_filled_chatterbox_w_before_and_count(self):
        from datetime import datetime
        from datetime import timedelta
        from karl.views.chatter import TIMEAGO_FORMAT
        now = datetime.utcnow()
        _registerSecurityPolicy('user')
        site = testing.DummyModel()
        quips = []
        for i in range(30):
            # from 15 sec ago to 14 sec in the future
            when = now + timedelta(0, i - 15)
            quips.append(DummyQuip(str(i), created=when))
        quips.reverse() # get them in recency-order
        site['chatter'] = context = _makeChatterbox(quips)
        request = testing.DummyRequest(
                    GET={'before': now.strftime(TIMEAGO_FORMAT), 'count': 5})
        info = self._callFUT(context, request)
        _verify_quips(info['recent'], quips[15:20], request)


class Test_all_chatter(unittest.TestCase):

    def _callFUT(self, context, request):
        from karl.views.chatter import all_chatter
        return all_chatter(context, request)

    def test_empty_chatterbox(self):
        site = testing.DummyModel()
        site['chatter'] = context = _makeChatterbox()
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        self.assertEqual(info['api'].page_title, 'All Chatter')
        self.assertEqual(info['chatter_form_url'],
                         'http://example.com/chatter/add_chatter.html')
        self.assertEqual(info['recent'], [])


class Test_followed_chatter_json(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        from karl.views.chatter import followed_chatter_json
        return followed_chatter_json(context, request)

    def test_empty_chatterbox(self):
        _registerSecurityPolicy('user')
        site = testing.DummyModel()
        site['chatter'] = context = _makeChatterbox()
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        self.assertEqual(info['recent'], [])
        self.assertEqual(context._followed, 'user')
        self.failIf(context._tag or context._names or
                    context._community or context._creators)

    def test_filled_chatterbox(self):
        _registerSecurityPolicy('user')
        site = testing.DummyModel()
        quips = [DummyQuip('1'), DummyQuip('2'), DummyQuip('3')]
        site['chatter'] = context = _makeChatterbox(quips)
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        _verify_quips(info['recent'], quips, request)

    def test_filled_chatterbox_skips_unauthorized_private_quips(self):
        _registerSecurityPolicy('user', permissive=False)
        site = testing.DummyModel()
        quips = [DummyQuip('1'), DummyQuip('2'), DummyQuip('3')]
        site['chatter'] = context = _makeChatterbox(quips)
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        self.assertEqual(info['recent'], [])

    def test_overfilled_chatterbox(self):
        _registerSecurityPolicy('user')
        site = testing.DummyModel()
        quips = []
        for i in range(30):
            quips.append(DummyQuip(str(i)))
        site['chatter'] = context = _makeChatterbox(quips)
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        _verify_quips(info['recent'], quips[:20], request)

    def test_filled_chatterbox_w_start_and_count(self):
        _registerSecurityPolicy('user')
        site = testing.DummyModel()
        quips = []
        for i in range(30):
            quips.append(DummyQuip(str(i)))
        site['chatter'] = context = _makeChatterbox(quips)
        request = testing.DummyRequest(GET={'start': 2, 'count': 5})
        info = self._callFUT(context, request)
        _verify_quips(info['recent'], quips[2:7], request)


class Test_followed_chatter(unittest.TestCase):

    def _callFUT(self, context, request):
        from karl.views.chatter import followed_chatter
        return followed_chatter(context, request)

    def test_empty_chatterbox(self):
        site = testing.DummyModel()
        site['chatter'] = context = _makeChatterbox()
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        self.assertEqual(info['api'].page_title, 'Recent Chatter')
        self.assertEqual(info['chatter_form_url'],
                         'http://example.com/chatter/add_chatter.html')
        self.assertEqual(info['recent'], [])


class Test_creators_chatter_json(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

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
        self.failIf(context._names or context._tag or
                    context._followed or context._community)

    def test_filled_chatterbox_creators_as_tuple(self):
        site = testing.DummyModel()
        quips = [DummyQuip('1'), DummyQuip('2'), DummyQuip('3')]
        site['chatter'] = context = _makeChatterbox(quips)
        request = testing.DummyRequest(GET={'creators': ('USER',)})
        info = self._callFUT(context, request)
        self.assertEqual(info['creators'], ['USER'])
        _verify_quips(info['recent'], quips, request)

    def test_filled_chatterbox_skips_unauthorized_private_quips(self):
        _registerSecurityPolicy('user', permissive=False)
        site = testing.DummyModel()
        quips = [DummyQuip('1'), DummyQuip('2'), DummyQuip('3')]
        site['chatter'] = context = _makeChatterbox(quips)
        request = testing.DummyRequest(GET={'creators': ('USER',)})
        info = self._callFUT(context, request)
        self.assertEqual(info['recent'], [])

    def test_overfilled_chatterbox(self):
        site = testing.DummyModel()
        quips = []
        for i in range(30):
            quips.append(DummyQuip(str(i)))
        site['chatter'] = context = _makeChatterbox(quips)
        request = testing.DummyRequest(GET={'creators': ['USER', 'USER2']})
        info = self._callFUT(context, request)
        self.assertEqual(info['creators'], ['USER', 'USER2'])
        _verify_quips(info['recent'], quips[:20], request)
        self.assertEqual(context._creators, ('USER', 'USER2'))
        self.failIf(context._names or context._tag or context._followed or
                    context._community)

    def test_filled_chatterbox_w_start_and_count(self):
        site = testing.DummyModel()
        quips = []
        for i in range(30):
            quips.append(DummyQuip(str(i)))
        site['chatter'] = context = _makeChatterbox(quips)
        request = testing.DummyRequest(GET={'creators': ['USER', 'USER2'],
                                            'start': 2, 'count': 5})
        info = self._callFUT(context, request)
        _verify_quips(info['recent'], quips[2:7], request)


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
        self.assertEqual(info['chatter_form_url'],
                         'http://example.com/chatter/add_chatter.html')
        self.assertEqual(info['recent'], [])

    def test_empty_chatterbox_creators_as_list(self):
        site = testing.DummyModel()
        site['chatter'] = context = _makeChatterbox()
        request = testing.DummyRequest(GET={'creators': ['USER', 'USER2']})
        info = self._callFUT(context, request)
        self.assertEqual(info['creators'], ['USER', 'USER2'])
        self.assertEqual(info['api'].page_title, 'Chatter: @USER, @USER2')
        self.assertEqual(info['recent'], [])


class Test_names_chatter_json(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

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
        self.failIf(context._creators or context._tag or context._followed
                    or context._community)

    def test_filled_chatterbox_names_as_tuple(self):
        site = testing.DummyModel()
        quips = [DummyQuip('1'), DummyQuip('2'), DummyQuip('3')]
        site['chatter'] = context = _makeChatterbox(quips)
        request = testing.DummyRequest(GET={'names': ('USER',)})
        info = self._callFUT(context, request)
        self.assertEqual(info['names'], ['USER'])
        _verify_quips(info['recent'], quips, request)
        self.assertEqual(context._names, ('USER',))

    def test_filled_chatterbox_skips_unauthorized_private_quips(self):
        _registerSecurityPolicy('user', permissive=False)
        site = testing.DummyModel()
        quips = [DummyQuip('1'), DummyQuip('2'), DummyQuip('3')]
        site['chatter'] = context = _makeChatterbox(quips)
        request = testing.DummyRequest(GET={'names': ('USER',)})
        info = self._callFUT(context, request)
        self.assertEqual(info['recent'], [])

    def test_overfilled_chatterbox(self):
        site = testing.DummyModel()
        quips = []
        for i in range(30):
            quips.append(DummyQuip(str(i)))
        site['chatter'] = context = _makeChatterbox(quips)
        request = testing.DummyRequest(GET={'names': ['USER', 'USER2']})
        info = self._callFUT(context, request)
        self.assertEqual(info['names'], ['USER', 'USER2'])
        _verify_quips(info['recent'], quips[:20], request)
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
        _verify_quips(info['recent'], quips[2:7], request)


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
        self.assertEqual(info['chatter_form_url'],
                         'http://example.com/chatter/add_chatter.html')
        self.assertEqual(info['recent'], [])

    def test_empty_chatterbox_names_as_list(self):
        site = testing.DummyModel()
        site['chatter'] = context = _makeChatterbox()
        request = testing.DummyRequest(GET={'names': ['USER', 'USER2']})
        info = self._callFUT(context, request)
        self.assertEqual(info['names'], ['USER', 'USER2'])
        self.assertEqual(info['api'].page_title, 'Chatter: @USER, @USER2')
        self.assertEqual(info['recent'], [])


class Test_tag_chatter_json(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

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
        self.failIf(context._names or context._followed or
                    context._community or context._creators)

    def test_filled_chatterbox(self):
        site = testing.DummyModel()
        quips = [DummyQuip('1'), DummyQuip('2'), DummyQuip('3')]
        site['chatter'] = context = _makeChatterbox(quips)
        request = testing.DummyRequest(GET={'tag': 'sometag'})
        info = self._callFUT(context, request)
        _verify_quips(info['recent'], quips, request)

    def test_filled_chatterbox_skips_unauthorized_private_quips(self):
        _registerSecurityPolicy('user', permissive=False)
        site = testing.DummyModel()
        quips = [DummyQuip('1'), DummyQuip('2'), DummyQuip('3')]
        site['chatter'] = context = _makeChatterbox(quips)
        request = testing.DummyRequest(GET={'tag': 'sometag'})
        info = self._callFUT(context, request)
        self.assertEqual(info['recent'], [])

    def test_overfilled_chatterbox(self):
        site = testing.DummyModel()
        quips = []
        for i in range(30):
            quips.append(DummyQuip(str(i)))
        site['chatter'] = context = _makeChatterbox(quips)
        request = testing.DummyRequest(GET={'tag': 'sometag'})
        info = self._callFUT(context, request)
        _verify_quips(info['recent'], quips[:20], request)

    def test_filled_chatterbox_w_start_and_count(self):
        site = testing.DummyModel()
        quips = []
        for i in range(30):
            quips.append(DummyQuip(str(i)))
        site['chatter'] = context = _makeChatterbox(quips)
        request = testing.DummyRequest(GET={'tag': 'sometag',
                                            'start': 2, 'count': 5})
        info = self._callFUT(context, request)
        _verify_quips(info['recent'], quips[2:7], request)


class Test_tag_chatter(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

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
        self.assertEqual(info['chatter_form_url'],
                         'http://example.com/chatter/add_chatter.html')
        self.assertEqual(info['recent'], [])


class Test_community_chatter_json(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

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
        self.failIf(cb._names or cb._creators or cb._followed or cb._tag)

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
        _verify_quips(info['recent'], quips, request)

    def test_filled_chatterbox_skips_unauthorized_private_quips(self):
        _registerSecurityPolicy('user', permissive=False)
        site = testing.DummyModel()
        quips = [DummyQuip('1'), DummyQuip('2'), DummyQuip('3')]
        site['chatter'] = cb = _makeChatterbox(quips)
        site['communities'] = cf = testing.DummyModel()
        cf['testing'] = context = testing.DummyModel()
        site['communities'] = cf = testing.DummyModel()
        cf['testing'] = context = testing.DummyModel()
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        self.assertEqual(info['recent'], [])

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
        _verify_quips(info['recent'], quips[:20], request)

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
        _verify_quips(info['recent'], quips[2:7], request)


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
        self.assertEqual(info['chatter_form_url'],
                         'http://example.com/chatter/add_chatter.html')
        self.assertEqual(info['recent'], [])


class Test_update_followed(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        from karl.views.chatter import update_followed
        return update_followed(context, request)

    def test_GET(self):
        FOLLOWED = ['user1', 'user2', 'user3']
        _registerSecurityPolicy('user')
        site = testing.DummyModel()
        site['profiles'] = testing.DummyModel() # TemplateAPI requires it
        _called_with = []
        def _listFollowed(userid):
            _called_with.append(userid)
            return FOLLOWED
        site['chatter'] = context = _makeChatterbox()
        context.listFollowed = _listFollowed
        request = testing.DummyRequest(view_name='update_followed.html')
        info = self._callFUT(context, request)
        self.assertEqual(info['followed'], '\n'.join(FOLLOWED))
        self.assertEqual(info['view_url'],
                         'http://example.com/chatter/update_followed.html')
        self.assertEqual(_called_with, ['user'])

    def test_POST(self):
        BEFORE = ['user1', 'user2', 'user3']
        AFTER = ['user1', 'user2']
        _registerSecurityPolicy('user')
        site = testing.DummyModel()
        _called_with = []
        def _setFollowed(userid, followed):
            _called_with.append((userid, followed))
        site['chatter'] = context = _makeChatterbox()
        context.setFollowed = _setFollowed
        request = testing.DummyRequest()
        request.POST['followed'] = '\n'.join(AFTER)
        found = self._callFUT(context, request)
        self.assertEqual(found.location, 'http://example.com/chatter/')
        self.assertEqual(_called_with, [('user', AFTER)])


class Test_add_chatter(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        from karl.views.chatter import add_chatter
        return add_chatter(context, request)

    def test_POST(self):
        _registerSecurityPolicy('user')
        site = testing.DummyModel()
        site['chatter'] = context = _makeChatterbox()
        request = testing.DummyRequest()
        request.POST['text'] = 'This is a quip.'
        found = self._callFUT(context, request)
        self.assertEqual(found.location, 'http://example.com/chatter/')
        self.assertEqual(context._added.text, 'This is a quip.')
        self.assertEqual(context._added.creator, 'user')

    def test_POST_w_private(self):
        from pyramid.security import Allow
        from pyramid.security import DENY_ALL
        TEXT = 'Quip. @otheruser &testing'
        _registerSecurityPolicy('user')
        site = testing.DummyModel()
        site['chatter'] = context = _makeChatterbox()
        request = testing.DummyRequest()
        request.POST['text'] = TEXT
        request.POST['private'] = '1'
        found = self._callFUT(context, request)
        self.assertEqual(found.location, 'http://example.com/chatter/')
        self.assertEqual(context._added.text, TEXT)
        self.assertEqual(context._added.creator, 'user')
        self.assertEqual(context._added.__acl__,
                         [(Allow, 'view', 'user'),
                          (Allow, 'view', 'otheruser'),
                          (Allow, 'view', 'group.community:testing:members'),
                          DENY_ALL,
                         ])


def _makeChatterbox(recent=()):

    from karl.models.chatter import Quip

    class _Chatterbox(testing.DummyModel):
        _KEY = 'KEY'
        _names = _tag = _community = _added = _creators = _followed = None
        def __init__(self, recent):
            self._recent = recent
        def addQuip(self, text, creator):
            self._added = Quip(text=text, creator=creator)
            return self._KEY
        def __getitem__(self, key):
            if key == self._KEY:
                return self._added
            raise KeyError
        def recent(self):
            return self._recent
        def recentFollowed(self, userid):
            self._followed = userid
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


def _registerSecurityPolicy(userid, groupids=(), permissive=True):
    karltesting.registerDummySecurityPolicy(userid, groupids, permissive)


_WHEN = object()

class DummyQuip(testing.DummyModel):
    __name__ = __parent__ = None
    def __init__(self, text='TEXT', creator='USER', created=_WHEN,
                 names=(), communities=(), tags=()):
        import datetime
        self.text = text
        self.creator = creator
        self.names = names
        self.communities = communities
        self.tags = tags
        if created is _WHEN:
            created = datetime.datetime(2012, 2, 23, 20, 29, 47) # XXX zone?
        self.created = created
    def __repr__(self):
        return '%s: %s, %s' % (self.__class__.__name__, self.text, self.creator)

class DummySecurityPolicy:
    """ A standin for both an IAuthentication and IAuthorization policy """
    def __init__(self, userid=None, groupids=(), permissions=None):
        self.userid = userid

    def authenticated_userid(self, request):
        return self.userid
