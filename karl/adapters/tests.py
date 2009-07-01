import unittest
from zope.testing.cleanup import cleanUp

class MailinDispatcherTests(unittest.TestCase):

    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from karl.adapters.mailin import MailinDispatcher
        return MailinDispatcher

    def _makeOne(self, context=None):
        if context is None:
            context = self._makeContext()
        return self._getTargetClass()(context)

    def _makeContext(self):
        from repoze.bfg.testing import DummyModel
        return DummyModel()

    def test_class_conforms_to_IMailinHandler(self):
        from zope.interface.verify import verifyClass
        from karl.adapters.interfaces import IMailinDispatcher
        verifyClass(IMailinDispatcher, self._getTargetClass())

    def test_instance_conforms_to_IMailinHandler(self):
        from zope.interface.verify import verifyObject
        from karl.adapters.interfaces import IMailinDispatcher
        verifyObject(IMailinDispatcher, self._makeOne())

    def test_getAddrList_none(self):
        mailin = self._makeOne()
        message = DummyMessage()
        message.get_all = lambda name: None
        self.assertEqual(list(mailin.getAddrList(message, 'nonesuch')), [])

    def test_getAddrList_one(self):
        mailin = self._makeOne()
        message = DummyMessage()
        message.get_all = lambda name: ['Phred Bloggs <phreddy@example.com>']
        self.assertEqual(list(mailin.getAddrList(message, 'From')),
                         [('Phred Bloggs', 'phreddy@example.com')])

    def test_getAddrList_multiple(self):
        mailin = self._makeOne()
        message = DummyMessage()
        message.get_all = lambda name: ['Phred Bloggs <phreddy@example.com>',
                                        'Sally Port <sally@example.com>',
                                       ]
        self.assertEqual(list(mailin.getAddrList(message, 'To')),
                         [('Phred Bloggs', 'phreddy@example.com'),
                          ('Sally Port', 'sally@example.com'),
                         ])

    def test_isCommunity_nonesuch(self):
        context = self._makeContext()
        context['communities'] = self._makeContext()
        mailin = self._makeOne(context)
        self.failIf(mailin.isCommunity('nonesuch'))

    def test_isCommunity_extant(self):
        context = self._makeContext()
        cf = context['communities'] = self._makeContext()
        cf['extant'] = self._makeContext()
        mailin = self._makeOne(context)
        self.failUnless(mailin.isCommunity('extant'))

    def test_getCommunityId_nonesuch(self):
        context = self._makeContext()
        context['communities'] = self._makeContext()
        mailin = self._makeOne(context)
        self.assertEqual(mailin.getCommunityId('nonesuch@example.com'), None)

    def test_getCommunityId_extant(self):
        context = self._makeContext()
        cf = context['communities'] = self._makeContext()
        cf['extant'] = self._makeContext()
        mailin = self._makeOne(context)
        self.assertEqual(mailin.getCommunityId('extant@example.com'), 'extant')

    def test_getAuthor_nonesuch(self):
        context = self._makeContext()
        pf = context['profiles'] = self._makeContext()
        pf.getProfileByEmail = lambda email: None
        mailin = self._makeOne(context)
        self.assertEqual(mailin.getAuthor('nonesuch@example.com'), None)

    def test_getAuthor_extant(self):
        context = self._makeContext()
        profile = self._makeContext()
        profile.__name__ = 'extant'
        by_email = {'extant@example.com': profile}
        pf = context['profiles'] = self._makeContext()
        pf.getProfileByEmail = lambda email: by_email.get(email)
        mailin = self._makeOne(context)
        self.assertEqual(mailin.getAuthor('extant@example.com'), 'extant')

    def test_crackHeaders_no_To(self):
        mailin = self._makeOne()
        message = DummyMessage()
        info = mailin.crackHeaders(message)
        self.failUnless(info['bounce'])
        self.assertEqual(info['reason'], 'missing To:')

    def test_crackHeaders_no_From(self):
        mailin = self._makeOne()
        message = DummyMessage()
        message.to = ('community@example.com',)
        info = mailin.crackHeaders(message)
        self.failUnless(info['bounce'])
        self.assertEqual(info['reason'], 'missing From:')

    def test_crackHeaders_multiple_From(self):
        mailin = self._makeOne()
        message = DummyMessage()
        message.to = ('community@example.com',)
        message.from_ = ('member1@example.com',
                         'member2@example.com',
                        )
        info = mailin.crackHeaders(message)
        self.failUnless(info['bounce'])
        self.assertEqual(info['reason'], 'multiple From:')

    def test_crackHeaders_no_subject(self):
        mailin = self._makeOne()
        message = DummyMessage()
        message.to = ('community@example.com',)
        message.from_ = ('extant@example.com',)

        info = mailin.crackHeaders(message)
        self.failUnless(info['bounce'])
        self.assertEqual(info['reason'], 'missing Subject:')

    def test_crackHeaders_vacation(self):
        mailin = self._makeOne()
        message = DummyMessage()
        message.to = ('community@example.com',)
        message.from_ = ('extant@example.com',)
        message.subject = 'Out of Office AutoReply'

        info = mailin.crackHeaders(message)
        self.failUnless(info['bounce'])
        self.assertEqual(info['reason'], 'vacation message')

    def test_crackHeaders_bad_author(self):
        context = self._makeContext()
        by_email = {}
        pf = context['profiles'] = self._makeContext()
        pf.getProfileByEmail = lambda email: by_email.get(email)
        mailin = self._makeOne(context)
        message = DummyMessage()
        message.to = ('community@example.com',)
        message.from_ = ('nonesuch@example.com',)
        message.subject = 'subject'

        info = mailin.crackHeaders(message)
        self.failUnless(info['bounce'])
        self.assertEqual(info['reason'], 'author not found')

    def test_crackHeaders_reply_invalid_community(self):
        context = self._makeContext()
        profile = self._makeContext()
        profile.__name__ = 'extant'
        by_email = {'extant@example.com': profile}
        pf = context['profiles'] = self._makeContext()
        pf.getProfileByEmail = lambda email: by_email.get(email)
        context['communities'] = self._makeContext()
        mailin = self._makeOne(context)
        message = DummyMessage()
        message.to = ('nonesuch+tool-12345@example.com',)
        message.from_ = ('extant@example.com',)
        message.subject = 'subject'

        info = mailin.crackHeaders(message)
        self.failUnless(info['bounce'])
        self.assertEqual(info['reason'], 'invalid community: nonesuch')
        self.assertEqual(info['community'], 'nonesuch')
        self.assertEqual(info['tool'], 'tool')
        self.assertEqual(info['in_reply_to'], '12345')
        self.assertEqual(info['author'], 'extant')
        self.assertEqual(info['subject'], 'subject')

    def test_crackHeaders_reply_invalid_to_addr(self):
        context = self._makeContext()
        profile = self._makeContext()
        profile.__name__ = 'extant'
        by_email = {'extant@example.com': profile}
        pf = context['profiles'] = self._makeContext()
        pf.getProfileByEmail = lambda email: by_email.get(email)
        context['communities'] = self._makeContext()
        mailin = self._makeOne(context)
        message = DummyMessage()
        message.to = ('undisclosed-recipients:;',)
        message.from_ = ('extant@example.com',)
        message.subject = 'subject'

        info = mailin.crackHeaders(message)
        self.failUnless(info['bounce'])
        self.assertEqual(info['reason'], 'no community')
        self.assertEqual(info['community'], None)
        self.assertEqual(info['tool'], None)
        self.assertEqual(info['in_reply_to'], None)
        self.assertEqual(info['author'], 'extant')
        self.assertEqual(info['subject'], 'subject')

    def test_crackHeaders_reply_ok(self):
        context = self._makeContext()
        profile = self._makeContext()
        profile.__name__ = 'extant'
        by_email = {'extant@example.com': profile}
        pf = context['profiles'] = self._makeContext()
        pf.getProfileByEmail = lambda email: by_email.get(email)
        cf = context['communities'] = self._makeContext()
        cf['testing'] = self._makeContext()
        mailin = self._makeOne(context)
        message = DummyMessage()
        message.to = ('testing+tool-12345@example.com',)
        message.from_ = ('extant@example.com',)
        message.subject = 'subject'
        message.content_type = 'text/plain'

        info = mailin.crackHeaders(message)
        self.failIf(info['bounce'])
        self.assertEqual(info['community'], 'testing')
        self.assertEqual(info['tool'], 'tool')
        self.assertEqual(info['in_reply_to'], '12345')
        self.assertEqual(info['author'], 'extant')
        self.assertEqual(info['subject'], 'subject')

    def test_crackHeaders_reply_ok_community_with_hyphen(self):
        context = self._makeContext()
        profile = self._makeContext()
        profile.__name__ = 'extant'
        by_email = {'extant@example.com': profile}
        pf = context['profiles'] = self._makeContext()
        pf.getProfileByEmail = lambda email: by_email.get(email)
        cf = context['communities'] = self._makeContext()
        cf['with-hyphen'] = self._makeContext()
        mailin = self._makeOne(context)
        message = DummyMessage()
        message.to = ('with-hyphen+tool-12345@example.com',)
        message.from_ = ('extant@example.com',)
        message.subject = 'subject'
        message.content_type = 'text/plain'

        info = mailin.crackHeaders(message)
        self.failIf(info['bounce'])
        self.assertEqual(info['community'], 'with-hyphen')
        self.assertEqual(info['tool'], 'tool')
        self.assertEqual(info['in_reply_to'], '12345')
        self.assertEqual(info['author'], 'extant')
        self.assertEqual(info['subject'], 'subject')

    def test_crackHeaders_tool_invalid_community(self):
        context = self._makeContext()
        profile = self._makeContext()
        profile.__name__ = 'extant'
        by_email = {'extant@example.com': profile}
        pf = context['profiles'] = self._makeContext()
        pf.getProfileByEmail = lambda email: by_email.get(email)
        context['communities'] = self._makeContext()
        mailin = self._makeOne(context)
        message = DummyMessage()
        message.to = ('nonesuch+tool@example.com',)
        message.from_ = ('extant@example.com',)
        message.subject = 'subject'

        info = mailin.crackHeaders(message)
        self.failUnless(info['bounce'])
        self.assertEqual(info['reason'], 'invalid community: nonesuch')
        self.assertEqual(info['community'], 'nonesuch')
        self.assertEqual(info['tool'], 'tool')
        self.assertEqual(info['in_reply_to'], None)
        self.assertEqual(info['author'], 'extant')
        self.assertEqual(info['subject'], 'subject')

    def test_crackHeaders_tool_ok(self):
        context = self._makeContext()
        profile = self._makeContext()
        profile.__name__ = 'extant'
        by_email = {'extant@example.com': profile}
        pf = context['profiles'] = self._makeContext()
        pf.getProfileByEmail = lambda email: by_email.get(email)
        cf = context['communities'] = self._makeContext()
        cf['testing'] = self._makeContext()
        mailin = self._makeOne(context)
        message = DummyMessage()
        message.to = ('testing+tool@example.com',)
        message.from_ = ('extant@example.com',)
        message.subject = 'subject'

        info = mailin.crackHeaders(message)
        self.failIf(info['bounce'])
        self.assertEqual(info['community'], 'testing')
        self.assertEqual(info['tool'], 'tool')
        self.assertEqual(info['in_reply_to'], None)
        self.assertEqual(info['author'], 'extant')
        self.assertEqual(info['subject'], 'subject')

    def test_crackHeaders_tool_ok_community_with_hyphen(self):
        context = self._makeContext()
        profile = self._makeContext()
        profile.__name__ = 'extant'
        by_email = {'extant@example.com': profile}
        pf = context['profiles'] = self._makeContext()
        pf.getProfileByEmail = lambda email: by_email.get(email)
        cf = context['communities'] = self._makeContext()
        cf['with-hyphen'] = self._makeContext()
        mailin = self._makeOne(context)
        message = DummyMessage()
        message.to = ('with-hyphen+tool@example.com',)
        message.from_ = ('extant@example.com',)
        message.subject = 'subject'

        info = mailin.crackHeaders(message)
        self.failIf(info['bounce'], info)
        self.assertEqual(info['community'], 'with-hyphen')
        self.assertEqual(info['tool'], 'tool')
        self.assertEqual(info['in_reply_to'], None)
        self.assertEqual(info['author'], 'extant')
        self.assertEqual(info['subject'], 'subject')

    def test_crackHeaders_default_invalid_community(self):
        context = self._makeContext()
        profile = self._makeContext()
        profile.__name__ = 'extant'
        by_email = {'extant@example.com': profile}
        pf = context['profiles'] = self._makeContext()
        pf.getProfileByEmail = lambda email: by_email.get(email)
        context['communities'] = self._makeContext()
        mailin = self._makeOne(context)
        mailin.default_tool = 'default'
        message = DummyMessage()
        message.to = ('nonesuch@example.com',)
        message.from_ = ('extant@example.com',)
        message.subject = 'subject'

        info = mailin.crackHeaders(message)
        self.failUnless(info['bounce'])
        self.assertEqual(info['reason'], 'no community')
        self.assertEqual(info['community'], None)
        self.assertEqual(info['tool'], 'default')
        self.assertEqual(info['in_reply_to'], None)
        self.assertEqual(info['author'], 'extant')
        self.assertEqual(info['subject'], 'subject')

    def test_crackHeaders_default_ok(self):
        context = self._makeContext()
        profile = self._makeContext()
        profile.__name__ = 'extant'
        by_email = {'extant@example.com': profile}
        pf = context['profiles'] = self._makeContext()
        pf.getProfileByEmail = lambda email: by_email.get(email)
        cf = context['communities'] = self._makeContext()
        cf['testing'] = self._makeContext()
        mailin = self._makeOne(context)
        mailin.default_tool = 'default'
        message = DummyMessage()
        message.to = ('testing@example.com',)
        message.from_ = ('extant@example.com',)
        message.subject = 'subject'

        info = mailin.crackHeaders(message)
        self.failIf(info['bounce'])
        self.assertEqual(info['community'], 'testing')
        self.assertEqual(info['tool'], 'default')
        self.assertEqual(info['in_reply_to'], None)
        self.assertEqual(info['author'], 'extant')
        self.assertEqual(info['subject'], 'subject')

    def test_crackHeaders_default_community_in_CC(self):
        context = self._makeContext()
        profile = self._makeContext()
        profile.__name__ = 'extant'
        by_email = {'extant@example.com': profile}
        pf = context['profiles'] = self._makeContext()
        pf.getProfileByEmail = lambda email: by_email.get(email)
        cf = context['communities'] = self._makeContext()
        cf['testing'] = self._makeContext()
        mailin = self._makeOne(context)
        mailin.default_tool = 'default'
        message = DummyMessage()
        message.to = ('phreddy@example.com',)
        message.cc = ('testing@example.com',)
        message.from_ = ('extant@example.com',)
        message.subject = 'subject'

        info = mailin.crackHeaders(message)
        self.failIf(info['bounce'])
        self.assertEqual(info['community'], 'testing')
        self.assertEqual(info['tool'], 'default')
        self.assertEqual(info['in_reply_to'], None)
        self.assertEqual(info['author'], 'extant')
        self.assertEqual(info['subject'], 'subject')

    def test_crackPayload_empty(self):
        mailin = self._makeOne()
        message = DummyMessage()

        text, attachments = mailin.crackPayload(message)

        self.assertEqual(text, None)
        self.assertEqual(len(attachments), 0)

    def test_crackPayload_single(self):
        mailin = self._makeOne()
        message = DummyMessage()
        message.payload = 'payload'
        message.content_type = 'text/plain'

        text, attachments = mailin.crackPayload(message)

        self.assertEqual(text, u'payload')
        self.assertEqual(len(attachments), 0)

    def test_crackPayload_single_with_scrubber(self):
        from repoze.bfg.testing import registerUtility
        from karl.utilities.interfaces import IMailinTextScrubber
        _called_with = []
        def _fooScrubber(text, text_mimetype=None):
            _called_with.append((text, text_mimetype))
            return text.upper()
        registerUtility(_fooScrubber, IMailinTextScrubber, 'foo')
        mailin = self._makeOne()
        mailin.text_scrubber = 'foo'
        message = DummyMessage()
        message.payload = 'payload'
        message.content_type = 'text/plain'

        text, attachments = mailin.crackPayload(message)

        self.assertEqual(text, u'PAYLOAD')
        self.assertEqual(len(attachments), 0)
        self.assertEqual(len(_called_with), 1)
        self.assertEqual(_called_with[0][0], 'payload')
        self.assertEqual(_called_with[0][1], 'text/plain')

    def test_crackPayload_single_encoded(self):
        mailin = self._makeOne()
        message = DummyMessage()
        message.payload = 'payload'
        message.content_type = 'text/plain'
        message.charset = 'rot13'

        text, attachments = mailin.crackPayload(message)

        self.assertEqual(text, u'cnlybnq')
        self.assertEqual(len(attachments), 0)

    def test_crackPayload_multiple_no_attachments(self):
        mailin = self._makeOne()
        message = DummyMessage()
        part = DummyMessage()
        part.payload = 'payload'
        part.content_type = 'text/plain'
        message.payload = (part,)

        text, attachments = mailin.crackPayload(message)

        self.assertEqual(text, u'payload')
        self.assertEqual(len(attachments), 0)

    def test_crackPayload_multiple_skips_html(self):
        mailin = self._makeOne()
        message = DummyMessage()
        htmlpart = DummyMessage()
        htmlpart.payload = '<h1>payload</h1>'
        htmlpart.content_type = 'text/html'
        textpart = DummyMessage()
        textpart.payload = 'payload'
        textpart.content_type = 'text/plain'
        message.payload = (htmlpart, textpart)

        text, attachments = mailin.crackPayload(message)

        self.assertEqual(text, u'payload')
        self.assertEqual(len(attachments), 0)

    def test_crackPayload_multiple_no_text(self):
        mailin = self._makeOne()
        message = DummyMessage()
        file1part = DummyMessage()
        file1part.filename = 'file1.bin'
        file1part.payload = '0123456789ABCDEF'
        file1part.content_type = 'application/octet-stream'
        file2part = DummyMessage()
        file2part.filename = 'file2.png'
        file2part.payload = '0123456789abcdef'
        file2part.content_type = 'image/png'
        message.payload = (file1part, file2part)

        text, attachments = mailin.crackPayload(message)

        self.assertEqual(text, None)
        self.assertEqual(len(attachments), 2)
        filename, mimetype, data = attachments[0]
        self.assertEqual(filename, 'file1.bin')
        self.assertEqual(mimetype, 'application/octet-stream')
        self.assertEqual(data, '0123456789ABCDEF')
        filename, mimetype, data = attachments[1]
        self.assertEqual(filename, 'file2.png')
        self.assertEqual(mimetype, 'image/png')
        self.assertEqual(data, '0123456789abcdef')

    def test_crackPayload_multiple_w_text(self):
        from repoze.bfg.testing import registerUtility
        from karl.utilities.interfaces import IMailinTextScrubber
        _called_with = []
        def _fooScrubber(text, text_mimetype=None):
            _called_with.append((text, text_mimetype))
            return text.upper()
        registerUtility(_fooScrubber, IMailinTextScrubber, 'foo')
        mailin = self._makeOne()
        mailin.text_scrubber = 'foo'
        message = DummyMessage()
        filepart = DummyMessage()
        filepart.filename = 'file1.bin'
        filepart.payload = '0123456789ABCDEF'
        filepart.content_type = 'application/octet-stream'
        textpart = DummyMessage()
        textpart.payload = 'payload'
        textpart.charset = 'rot13'
        textpart.content_type = 'text/plain'
        message.payload = (filepart, textpart)

        text, attachments = mailin.crackPayload(message)

        self.assertEqual(text, u'CNLYBNQ')
        self.assertEqual(len(attachments), 1)
        filename, mimetype, data = attachments[0]
        self.assertEqual(filename, 'file1.bin')
        self.assertEqual(mimetype, 'application/octet-stream')
        self.assertEqual(data, '0123456789ABCDEF')
        self.assertEqual(len(_called_with), 1)
        self.assertEqual(_called_with[0][0], 'cnlybnq')
        self.assertEqual(_called_with[0][1], 'text/plain')

class TestOfflineContextURL(unittest.TestCase):
    def setUp(self):
        cleanUp()
        from karl.testing import registerSettings
        registerSettings()

    def tearDown(self):
        cleanUp()

    def _make_one(self, model):
        from karl.adapters.url import OfflineContextURL
        return OfflineContextURL(model, None)

    def test_it(self):
        from repoze.bfg.testing import DummyModel
        context = DummyModel()
        url = self._make_one(context)
        self.assertEqual(url(), 'http://offline.example.com/app/')

    def test_it_again(self):
        from repoze.bfg.testing import DummyModel
        parent = DummyModel()
        context = parent['foo'] = DummyModel()
        url = self._make_one(context)
        self.assertEqual(url(), 'http://offline.example.com/app/foo')

    def test_it_w_feeling(self):
        from repoze.bfg.testing import DummyModel
        parent = DummyModel()
        foo = parent['foo'] = DummyModel()
        context = foo['bar'] = DummyModel()
        url = self._make_one(context)
        self.assertEqual(url(), 'http://offline.example.com/app/foo/bar')


class DummyMessage:
    to = None
    from_ = None
    subject = None
    payload = ()
    content_type = None
    charset = None
    filename = None

    def _munge(self, name):
        name = name.lower()
        if name == 'from':
            name = 'from_'
        return name

    def get_all(self, name, failobj=None):
        name = self._munge(name)
        return getattr(self, name, failobj)

    def __getitem__(self, key):
        key = self._munge(key)
        return getattr(self, key)

    def walk(self):
        if isinstance(self.payload, basestring):
            yield self
        else:
            for part in self.payload:
                yield part
        raise StopIteration

    def get_filename(self):
        return self.filename

    def get_content_type(self):
        return self.content_type

    def get_content_charset(self):
        return self.charset

    def get_payload(self, i=None, decode=False):
        return self.payload
