import unittest
from pyramid import testing

class MailinDispatcherTests(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

        import datetime
        from karl.adapters import mailin
        self._save_datetime = mailin.datetime

        class DummyDateTime(object):
            def __init__(self):
                self.datetime = self
            def now(self):
                return datetime.datetime(1975, 7, 7, 7, 30)
            def __call__(self, *args):
                return datetime.datetime(*args)

        mailin.datetime = DummyDateTime()

    def tearDown(self):
        testing.cleanUp()

        from karl.adapters import mailin
        mailin.datetime = self._save_datetime
        mailin.ALIAS_REGX = None

    def _getTargetClass(self):
        from karl.adapters.mailin import MailinDispatcher
        return MailinDispatcher

    def _makeOne(self, context=None):
        if context is None:
            context = self._makeContext()
        return self._getTargetClass()(context)

    def _makeContext(self, **kw):
        from pyramid.testing import DummyModel
        return DummyModel(**kw)

    def _makeRoot(self):
        return self._makeContext(list_aliases={})

    def test_class_conforms_to_IMailinDispatcher(self):
        from zope.interface.verify import verifyClass
        from karl.adapters.interfaces import IMailinDispatcher
        verifyClass(IMailinDispatcher, self._getTargetClass())

    def test_instance_conforms_to_IMailinDispatcher(self):
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
        context = self._makeRoot()
        context['communities'] = self._makeContext()
        mailin = self._makeOne(context)
        self.failIf(mailin.isCommunity('nonesuch'))

    def test_isCommunity_extant(self):
        context = self._makeRoot()
        cf = context['communities'] = self._makeContext()
        cf['extant'] = self._makeContext()
        mailin = self._makeOne(context)
        self.failUnless(mailin.isCommunity('extant'))

    def test_isReport_nonesuch(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleDirectory
        context = self._makeRoot()
        pd = context['people'] = self._makeContext()
        directlyProvides(pd, IPeopleDirectory)
        mailin = self._makeOne(context)
        self.failIf(mailin.isReport('nonesuch'))

    def test_isReport_extant(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleDirectory
        context = self._makeRoot()
        pd = context['people'] = self._makeContext()
        directlyProvides(pd, IPeopleDirectory)
        pd['extant'] = self._makeContext()
        mailin = self._makeOne(context)
        self.failUnless(mailin.isReport('extant'))

    def test_isReport_subpath_miss(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleDirectory
        context = self._makeRoot()
        pd = context['people'] = self._makeContext()
        directlyProvides(pd, IPeopleDirectory)
        pd['section'] = self._makeContext()
        mailin = self._makeOne(context)
        self.failIf(mailin.isReport('section+nonesuch'))

    def test_isReport_subpath_hit(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleDirectory
        context = self._makeRoot()
        pd = context['people'] = self._makeContext()
        directlyProvides(pd, IPeopleDirectory)
        section = pd['section'] = self._makeContext()
        section['extant'] = self._makeContext()
        mailin = self._makeOne(context)
        self.failUnless(mailin.isReport('section+extant'))

    def test_isReport_alias(self):
        from pyramid.traversal import resource_path
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleDirectory
        context = self._makeRoot()
        pd = context['people'] = self._makeContext()
        directlyProvides(pd, IPeopleDirectory)
        section = pd['section'] = self._makeContext()
        extant = section['extant'] = self._makeContext()
        context.list_aliases['alias'] = resource_path(extant)
        mailin = self._makeOne(context)
        self.failUnless(mailin.isReport('alias'))

    def test_getCommunityId_nonesuch(self):
        context = self._makeRoot()
        context['communities'] = self._makeContext()
        mailin = self._makeOne(context)
        self.assertEqual(mailin.getCommunityId('nonesuch@example.com'), None)

    def test_getCommunityId_extant(self):
        context = self._makeRoot()
        cf = context['communities'] = self._makeContext()
        cf['extant'] = self._makeContext()
        mailin = self._makeOne(context)
        self.assertEqual(mailin.getCommunityId('extant@example.com'), 'extant')

    def test_getAuthor_nonesuch(self):
        context = self._makeRoot()
        pf = context['profiles'] = self._makeContext()
        pf.getProfileByEmail = lambda email: None
        mailin = self._makeOne(context)
        self.assertEqual(mailin.getAuthor('nonesuch@example.com'), None)

    def test_getAuthor_extant(self):
        context = self._makeRoot()
        profile = self._makeContext()
        profile.__name__ = 'extant'
        by_email = {'extant@example.com': profile}
        pf = context['profiles'] = self._makeContext()
        pf.getProfileByEmail = lambda email: by_email.get(email)
        mailin = self._makeOne(context)
        self.assertEqual(mailin.getAuthor('extant@example.com'), 'extant')

    def test_getMessageTargets_no_To(self):
        mailin = self._makeOne()
        message = DummyMessage()
        info = mailin.getMessageTargets(message)

        self.assertEqual(info['error'],
                         'no community or distribution list specified')

    def test_getMessageTarget_ok_target_also_in_X_Original_To(self):
        context = self._makeRoot()
        cf = context['communities'] = self._makeContext()
        cf['testing'] = self._makeContext()
        mailin = self._makeOne(context)
        message = DummyMessage()
        message.to = ('Testing Tool <testing+tool-12345A@example.com>',)
        message.x_original_to = ('testing+tool-12345a@example.com',)

        info = mailin.getMessageTargets(message)

        self.failIf(info.get('error'))
        targets = info['targets']
        self.assertEqual(len(targets), 1)
        info = targets[0]
        self.assertEqual(info['report'], None)
        self.assertEqual(info['community'], 'testing')
        self.assertEqual(info['tool'], 'tool')
        self.assertEqual(info['in_reply_to'], '12345A')

    def test_getMessageTargets_reply_invalid_community(self):
        context = self._makeRoot()
        context['communities'] = self._makeContext()
        mailin = self._makeOne(context)
        message = DummyMessage()
        message.to = ('nonesuch+tool-12345@example.com',)

        info = mailin.getMessageTargets(message)

        self.assertEqual(info['error'],
                         'no community or distribution list specified')
        self.assertEqual(len(info['targets']), 1)
        target = info['targets'][0]
        self.assertEqual(target['report'], None)
        self.assertEqual(target['community'], 'nonesuch')
        self.assertEqual(target['tool'], 'tool')
        self.assertEqual(target['in_reply_to'], '12345')

    def test_getMessageTarget_reply_invalid_to_addr(self):
        context = self._makeRoot()
        context['communities'] = self._makeContext()
        mailin = self._makeOne(context)
        message = DummyMessage()
        message.to = ('undisclosed-recipients:;',)

        info = mailin.getMessageTargets(message)

        self.assertEqual(info['error'],
                         'no community or distribution list specified')
        self.assertEqual(len(info['targets']), 0)

    def test_getMessageTarget_reply_ok(self):
        context = self._makeRoot()
        cf = context['communities'] = self._makeContext()
        cf['testing'] = self._makeContext()
        mailin = self._makeOne(context)
        message = DummyMessage()
        message.to = ('testing+tool-12345@example.com',)

        info = mailin.getMessageTargets(message)

        self.failIf(info.get('error'))
        targets = info['targets']
        self.assertEqual(len(targets), 1)
        info = targets[0]
        self.assertEqual(info['report'], None)
        self.assertEqual(info['community'], 'testing')
        self.assertEqual(info['tool'], 'tool')
        self.assertEqual(info['in_reply_to'], '12345')

    def test_getMessageTarget_reply_ok_target_in_X_Original_To(self):
        context = self._makeRoot()
        cf = context['communities'] = self._makeContext()
        cf['testing'] = self._makeContext()
        mailin = self._makeOne(context)
        message = DummyMessage()
        message.x_original_to = ('testing+tool-12345@example.com',)

        info = mailin.getMessageTargets(message)

        self.failIf(info.get('error'))
        targets = info['targets']
        self.assertEqual(len(targets), 1)
        info = targets[0]
        self.assertEqual(info['report'], None)
        self.assertEqual(info['community'], 'testing')
        self.assertEqual(info['tool'], 'tool')
        self.assertEqual(info['in_reply_to'], '12345')

    def test_getMessageTarget_reply_ok_target_in_To_and_X_Original_To(self):
        context = self._makeRoot()
        cf = context['communities'] = self._makeContext()
        cf['testing'] = self._makeContext()
        mailin = self._makeOne(context)
        message = DummyMessage()
        message.to = ('Testing Tool <testing+tool-12345@example.com>',)
        message.x_original_to = ('testing+tool-12345@example.com',)

        info = mailin.getMessageTargets(message)

        self.failIf(info.get('error'))
        targets = info['targets']
        self.assertEqual(len(targets), 1)
        info = targets[0]
        self.assertEqual(info['report'], None)
        self.assertEqual(info['community'], 'testing')
        self.assertEqual(info['tool'], 'tool')
        self.assertEqual(info['in_reply_to'], '12345')

    def test_getMessageTarget_reply_ok_community_with_hyphen(self):
        context = self._makeRoot()
        cf = context['communities'] = self._makeContext()
        cf['with-hyphen'] = self._makeContext()
        mailin = self._makeOne(context)
        message = DummyMessage()
        message.to = ('with-hyphen+tool-12345@example.com',)

        info = mailin.getMessageTargets(message)

        self.failIf(info.get('error'))
        targets = info['targets']
        self.assertEqual(len(targets), 1)
        info = targets[0]
        self.assertEqual(info['report'], None)
        self.assertEqual(info['community'], 'with-hyphen')
        self.assertEqual(info['tool'], 'tool')
        self.assertEqual(info['in_reply_to'], '12345')

    def test_getMessageTarget_reply_ok_community_with_period(self):
        context = self._makeRoot()
        cf = context['communities'] = self._makeContext()
        cf['with-.dot'] = self._makeContext()
        mailin = self._makeOne(context)
        message = DummyMessage()
        message.to = ('with-.dot+tool-12345@example.com',)

        info = mailin.getMessageTargets(message)

        self.failIf(info.get('error'))
        targets = info['targets']
        self.assertEqual(len(targets), 1)
        info = targets[0]
        self.assertEqual(info['community'], 'with-.dot')
        self.assertEqual(info['tool'], 'tool')
        self.assertEqual(info['in_reply_to'], '12345')

    def test_getMessageTarget_tool_invalid_community(self):
        context = self._makeRoot()
        context['communities'] = self._makeContext()
        mailin = self._makeOne(context)
        message = DummyMessage()
        message.to = ('nonesuch+tool@example.com',)

        info = mailin.getMessageTargets(message)

        self.failUnless(info['error'])
        targets = info['targets']
        self.assertEqual(len(targets), 1)
        info = targets[0]
        self.assertEqual(info['error'], 'invalid community: nonesuch')
        self.assertEqual(info['report'], None)
        self.assertEqual(info['community'], 'nonesuch')
        self.assertEqual(info['tool'], 'tool')
        self.assertEqual(info['in_reply_to'], None)

    def test_getMessageTarget_tool_ok(self):
        context = self._makeRoot()
        cf = context['communities'] = self._makeContext()
        cf['testing'] = self._makeContext()
        mailin = self._makeOne(context)
        message = DummyMessage()
        message.to = ('testing+tool@example.com',)

        info = mailin.getMessageTargets(message)

        self.failIf(info.get('error'))
        targets = info['targets']
        self.assertEqual(len(targets), 1)
        info = targets[0]
        self.assertEqual(info['report'], None)
        self.assertEqual(info['community'], 'testing')
        self.assertEqual(info['tool'], 'tool')
        self.assertEqual(info['in_reply_to'], None)

    def test_getMessageTarget_tool_ok_community_with_hyphen(self):
        context = self._makeRoot()
        cf = context['communities'] = self._makeContext()
        cf['with-hyphen'] = self._makeContext()
        mailin = self._makeOne(context)
        message = DummyMessage()
        message.to = ('with-hyphen+tool@example.com',)

        info = mailin.getMessageTargets(message)

        self.failIf(info.get('error'), info)
        targets = info['targets']
        self.assertEqual(len(targets), 1)
        info = targets[0]
        self.assertEqual(info['report'], None)
        self.assertEqual(info['community'], 'with-hyphen')
        self.assertEqual(info['tool'], 'tool')
        self.assertEqual(info['in_reply_to'], None)

    def test_getMessageTarget_tool_ok_community_with_period(self):
        context = self._makeRoot()
        cf = context['communities'] = self._makeContext()
        cf['with-.dot'] = self._makeContext()
        mailin = self._makeOne(context)
        message = DummyMessage()
        message.to = ('with-.dot+tool@example.com',)

        info = mailin.getMessageTargets(message)

        self.failIf(info.get('error'), info)
        targets = info['targets']
        self.assertEqual(len(targets), 1)
        info = targets[0]
        self.assertEqual(info['community'], 'with-.dot')
        self.assertEqual(info['tool'], 'tool')
        self.assertEqual(info['in_reply_to'], None)

    def test_getMessageTarget_default_invalid_community(self):
        context = self._makeRoot()
        context['communities'] = self._makeContext()
        mailin = self._makeOne(context)
        mailin.default_tool = 'default'
        message = DummyMessage()
        message.to = ('nonesuch@example.com',)

        info = mailin.getMessageTargets(message)

        self.assertEqual(info['error'],
                         'no community or distribution list specified')
        self.assertEqual(len(info['targets']), 0)

    def test_getMessageTarget_default_valid_community(self):
        context = self._makeRoot()
        cf = context['communities'] = self._makeContext()
        cf['testing'] = self._makeContext()
        mailin = self._makeOne(context)
        mailin.default_tool = 'default'
        message = DummyMessage()
        message.to = ('testing@example.com',)

        info = mailin.getMessageTargets(message)

        self.failIf(info.get('error'))
        targets = info['targets']
        self.assertEqual(len(targets), 1)
        info = targets[0]
        self.assertEqual(info['report'], None)
        self.assertEqual(info['community'], 'testing')
        self.assertEqual(info['tool'], 'default')
        self.assertEqual(info['in_reply_to'], None)

    def test_getMessageTarget_report_reply_invalid_report(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleDirectory
        context = self._makeRoot()
        pd = context['people'] = self._makeContext()
        directlyProvides(pd, IPeopleDirectory)
        section = pd['section'] = self._makeContext()
        mailin = self._makeOne(context)
        message = DummyMessage()
        message.to = ('peopledir-section+nonesuch-12345@example.com',)

        info = mailin.getMessageTargets(message)

        self.failUnless(info['error'])
        targets = info['targets']
        self.assertEqual(len(targets), 1)
        info = targets[0]
        self.assertEqual(info['error'], 'invalid report: section+nonesuch')
        self.assertEqual(info['report'], 'section+nonesuch')
        self.assertEqual(info['community'], None)
        self.assertEqual(info['tool'], None)
        self.assertEqual(info['in_reply_to'], '12345')

    def test_getMessageTarget_report_reply_valid_report(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleDirectory
        context = self._makeRoot()
        pd = context['people'] = self._makeContext()
        directlyProvides(pd, IPeopleDirectory)
        section = pd['section'] = self._makeContext()
        section['extant'] = self._makeContext()
        mailin = self._makeOne(context)
        message = DummyMessage()
        message.to = ('peopledir-section+extant-12345@example.com',)

        info = mailin.getMessageTargets(message)

        self.failIf(info.get('error'), info)
        targets = info['targets']
        self.assertEqual(len(targets), 1)
        info = targets[0]
        self.assertEqual(info['report'], 'section+extant')
        self.assertEqual(info['community'], None)
        self.assertEqual(info['tool'], None)
        self.assertEqual(info['in_reply_to'], '12345')

    def test_getMessageTarget_report_invalid_report(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleDirectory
        context = self._makeRoot()
        pd = context['people'] = self._makeContext()
        directlyProvides(pd, IPeopleDirectory)
        section = pd['section'] = self._makeContext()
        mailin = self._makeOne(context)
        message = DummyMessage()
        message.to = ('peopledir-section+nonesuch@example.com',)

        info = mailin.getMessageTargets(message)

        self.failUnless(info['error'])
        targets = info['targets']
        self.assertEqual(len(targets), 1)
        info = targets[0]
        self.assertEqual(info['error'], 'invalid report: section+nonesuch')
        self.assertEqual(info['report'], 'section+nonesuch')
        self.assertEqual(info['community'], None)
        self.assertEqual(info['tool'], None)
        self.failIf(info.get('in_reply_to'), info)

    def test_getMessageTarget_report_valid_report(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleDirectory
        context = self._makeRoot()
        pd = context['people'] = self._makeContext()
        directlyProvides(pd, IPeopleDirectory)
        section = pd['section'] = self._makeContext()
        section['extant'] = self._makeContext()
        mailin = self._makeOne(context)
        message = DummyMessage()
        message.to = ('peopledir-section+extant@example.com',)

        info = mailin.getMessageTargets(message)

        self.failIf(info.get('error'), info)
        targets = info['targets']
        self.assertEqual(len(targets), 1)
        info = targets[0]
        self.assertEqual(info['report'], 'section+extant')
        self.assertEqual(info['community'], None)
        self.assertEqual(info['tool'], None)
        self.failIf(info.get('in_reply_to'), info)

    def test_getMessageTarget_report_alias(self):
        from pyramid.traversal import resource_path
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleDirectory
        context = self._makeRoot()
        pd = context['people'] = self._makeContext()
        directlyProvides(pd, IPeopleDirectory)
        section = pd['section'] = self._makeContext()
        extant = section['extant'] = self._makeContext()
        context.list_aliases['alias'] = resource_path(extant)
        mailin = self._makeOne(context)
        message = DummyMessage()
        message.to = ('alias@example.com',)

        info = mailin.getMessageTargets(message)

        self.failIf(info.get('error'), info)
        targets = info['targets']
        self.assertEqual(len(targets), 1)
        info = targets[0]
        self.assertEqual(info['report'], 'section+extant')
        self.assertEqual(info['community'], None)
        self.assertEqual(info['tool'], None)
        self.failIf(info.get('in_reply_to'), info)

    def test_getMessageTarget_report_alias_doesnt_shadow_community(self):
        from pyramid.interfaces import ISettings
        from pyramid.traversal import resource_path
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleDirectory
        from karl.testing import registerUtility
        settings = dict(system_list_subdomain = 'lists.example.com')
        registerUtility(settings, ISettings)
        context = self._makeRoot()
        cf = context['communities'] = self._makeContext()
        cf['testing'] = self._makeContext()
        pd = context['people'] = self._makeContext()
        directlyProvides(pd, IPeopleDirectory)
        section = pd['section'] = self._makeContext()
        extant = section['extant'] = self._makeContext()
        context.list_aliases['testing'] = resource_path(extant)
        mailin = self._makeOne(context)
        mailin.default_tool = 'default'
        message = DummyMessage()
        message.to = ('testing@example.com',)

        info = mailin.getMessageTargets(message)

        self.failIf(info.get('error'), info)
        targets = info['targets']
        self.assertEqual(len(targets), 1)
        info = targets[0]
        self.assertEqual(info['report'], None)
        self.assertEqual(info['community'], 'testing')
        self.assertEqual(info['tool'], 'default')
        self.assertEqual(info['in_reply_to'], None)

    def test_getMessageTarget_report_alias_w_subdomain(self):
        from pyramid.interfaces import ISettings
        from pyramid.traversal import resource_path
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleDirectory
        from karl.testing import registerUtility
        settings = dict(system_list_subdomain = 'lists.example.com')
        registerUtility(settings, ISettings)
        context = self._makeRoot()
        cf = context['communities'] = self._makeContext()
        cf['testing'] = self._makeContext()
        pd = context['people'] = self._makeContext()
        directlyProvides(pd, IPeopleDirectory)
        section = pd['section'] = self._makeContext()
        extant = section['extant'] = self._makeContext()
        context.list_aliases['testing'] = resource_path(extant)
        mailin = self._makeOne(context)
        message = DummyMessage()
        message.to = ('testing@lists.example.com',)

        info = mailin.getMessageTargets(message)

        self.failIf(info.get('error'), info)
        targets = info['targets']
        self.assertEqual(len(targets), 1)
        info = targets[0]
        self.assertEqual(info['report'], 'section+extant')
        self.assertEqual(info['community'], None)
        self.assertEqual(info['tool'], None)
        self.failIf(info.get('in_reply_to'), info)

    def test_getMessageAuthorAndSubject_no_From(self):
        mailin = self._makeOne()
        message = DummyMessage()
        info = mailin.getMessageAuthorAndSubject(message)
        self.assertEqual(info['error'], 'missing From:')

    def test_getMessageAuthorAndSubject_multiple_From(self):
        mailin = self._makeOne()
        message = DummyMessage()
        message.from_ = ('member1@example.com',
                         'member2@example.com',
                        )
        info = mailin.getMessageAuthorAndSubject(message)
        self.assertEqual(info['error'], 'multiple From:')

    def test_getMessageAuthorAndSubject_no_subject(self):
        context = self._makeRoot()
        profile = self._makeContext()
        profile.__name__ = 'extant'
        by_email = {'extant@example.com': profile}
        pf = context['profiles'] = self._makeContext()
        pf.getProfileByEmail = lambda email: by_email.get(email)
        mailin = self._makeOne(context)
        message = DummyMessage()
        message.from_ = ('extant@example.com',)

        info = mailin.getMessageAuthorAndSubject(message)
        self.assertEqual(info['error'], 'missing Subject:')

    def test_getMessageAuthorAndSubject_bad_author(self):
        context = self._makeRoot()
        by_email = {}
        pf = context['profiles'] = self._makeContext()
        pf.getProfileByEmail = lambda email: by_email.get(email)
        mailin = self._makeOne(context)
        message = DummyMessage()
        message.from_ = ('nonesuch@example.com',)
        message.subject = 'subject'

        info = mailin.getMessageAuthorAndSubject(message)
        self.assertEqual(info['error'], 'author not found')

    def test_getAutomationIndicators_precedence(self):
        mailin = self._makeOne()
        message = DummyMessage()
        message.precedence = 'bulk'

        info = mailin.getAutomationIndicators(message)
        self.assertEqual(info['error'], 'Precedence: bulk')

    def test_getAutomationIndicators_auto_submitted(self):
        mailin = self._makeOne()
        message = DummyMessage()
        setattr(message, 'auto-submitted', 'auto-generated')

        info = mailin.getAutomationIndicators(message)
        self.assertEqual(info['error'], 'Auto-Submitted: auto-generated')

    def test_getAutomationIndicators_vacation(self):
        mailin = self._makeOne()
        message = DummyMessage()
        message.subject = 'Out of Office AutoReply'

        info = mailin.getAutomationIndicators(message)
        self.assertEqual(info['error'], 'vacation message')

    def test_checkPermission_community_miss(self):
        from karl.testing import DummyUsers
        from karl.testing import registerDummySecurityPolicy
        registerDummySecurityPolicy('phred', permissive=False)
        context = self._makeRoot()
        communities = context['communities'] = self._makeContext()
        community = communities['testcommunity'] = self._makeContext()
        community['testtool'] = self._makeContext()
        users = context.users = DummyUsers()
        userinfo = users._by_id['phred'] = {}
        mailin = self._makeOne(context)
        info = {'author': 'phred',
                'targets': [{
                    'community': 'testcommunity',
                    'tool': 'testtool',
                    'report': None,
                    }, {
                    'error': 'Some other previous error',
                    }],
                }
        mailin.checkPermission(info)
        self.assertEqual(info['targets'][0]['error'], 'Permission Denied')
        self.assertEqual(info['targets'][1]['error'],
                         'Some other previous error')

    def test_checkPermission_community_hit(self):
        from karl.testing import DummyUsers
        from karl.testing import registerDummySecurityPolicy
        registerDummySecurityPolicy('phred', permissive=True)
        context = self._makeRoot()
        communities = context['communities'] = self._makeContext()
        community = communities['testcommunity'] = self._makeContext()
        community['testtool'] = self._makeContext()
        users = context.users = DummyUsers()
        userinfo = users._by_id['phred'] = {}
        mailin = self._makeOne(context)
        info = {'author': 'phred',
                'targets': [{
                    'community': 'testcommunity',
                    'tool': 'testtool',
                    'report': None,
                }]
               }
        mailin.checkPermission(info)
        self.failIf('error' in info['targets'][0])

    def test_checkPermission_report_miss(self):
        from zope.interface import directlyProvides
        from karl.testing import registerDummySecurityPolicy
        from karl.models.interfaces import IPeopleDirectory
        from karl.testing import DummyUsers
        registerDummySecurityPolicy('phred', permissive=False)
        context = self._makeRoot()
        pd = context['people'] = self._makeContext()
        directlyProvides(pd, IPeopleDirectory)
        section = pd['section'] = self._makeContext()
        report = section['report'] = self._makeContext()
        users = context.users = DummyUsers()
        userinfo = users._by_id['phred'] = {}
        mailin = self._makeOne(context)
        info = {'author': 'phred',
                'targets': [{
                    'community': None,
                    'tool': None,
                    'report': 'section+report',
                }]
               }
        mailin.checkPermission(info)
        self.assertEqual(info['targets'][0]['error'], 'Permission Denied')

    def test_checkPermission_report_hit(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IPeopleDirectory
        from karl.testing import DummyUsers
        from karl.testing import registerDummySecurityPolicy
        registerDummySecurityPolicy('phred', permissive=True)
        context = self._makeRoot()
        pd = context['people'] = self._makeContext()
        directlyProvides(pd, IPeopleDirectory)
        section = pd['section'] = self._makeContext()
        report = section['report'] = self._makeContext()
        users = context.users = DummyUsers()
        userinfo = users._by_id['phred'] = {}
        mailin = self._makeOne(context)
        info = {'author': 'phred',
                'targets': [{
                    'community': None,
                    'tool': None,
                    'report': 'section+report',
                }]
               }
        mailin.checkPermission(info)
        self.failIf('error' in info['targets'][0])

    def test_crackHeaders_no_To(self):
        mailin = self._makeOne()
        message = DummyMessage()
        info = mailin.crackHeaders(message)
        self.assertEqual(info['error'],
                         'no community or distribution list specified')

    def test_crackHeaders_no_From(self):
        context = self._makeRoot()
        cf = context['communities'] = self._makeContext()
        cf['testing'] = self._makeContext()
        mailin = self._makeOne(context)
        message = DummyMessage()
        message.to = ('testing+tool-12345@example.com',)

        info = mailin.crackHeaders(message)
        self.assertEqual(info['error'], 'missing From:')
        targets = info['targets']
        self.assertEqual(len(targets), 1)
        info = targets[0]
        self.assertEqual(info['community'], 'testing')
        self.assertEqual(info['tool'], 'tool')
        self.assertEqual(info['in_reply_to'], '12345')

    def test_crackHeaders_default_ok(self):
        import datetime
        from karl.testing import DummyUsers
        context = self._makeRoot()
        context.users = DummyUsers()
        profile = self._makeContext()
        profile.__name__ = 'extant'
        by_email = {'extant@example.com': profile}
        pf = context['profiles'] = self._makeContext()
        pf.getProfileByEmail = lambda email: by_email.get(email)
        cf = context['communities'] = self._makeContext()
        community = cf['testing'] = self._makeContext()
        tool = community['default'] = self._makeContext()
        mailin = self._makeOne(context)
        mailin.default_tool = 'default'
        message = DummyMessage()
        message.to = ('testing@example.com',)
        message.from_ = ('extant@example.com',)
        message.subject = 'subject'

        info = mailin.crackHeaders(message)
        self.failIf(info.get('error'))
        self.assertEqual(info['date'], datetime.datetime(1975, 7, 7, 7, 30))
        self.assertEqual(info['author'], 'extant')
        self.assertEqual(info['subject'], 'subject')
        targets = info['targets']
        self.assertEqual(len(targets), 1)
        info = targets[0]
        self.assertEqual(info['community'], 'testing')
        self.assertEqual(info['tool'], 'default')
        self.assertEqual(info['in_reply_to'], None)

    def test_crackHeaders_with_date_from_x_postoffice_date(self):
        import datetime
        from karl.testing import DummyUsers
        import time
        context = self._makeRoot()
        context.users = DummyUsers()
        profile = self._makeContext()
        profile.__name__ = 'extant'
        by_email = {'extant@example.com': profile}
        pf = context['profiles'] = self._makeContext()
        pf.getProfileByEmail = lambda email: by_email.get(email)
        cf = context['communities'] = self._makeContext()
        community = cf['testing'] = self._makeContext()
        tool = community['default'] = self._makeContext()
        mailin = self._makeOne(context)
        mailin.default_tool = 'default'
        message = DummyMessage()
        message.to = ('testing@example.com',)
        message.from_ = ('extant@example.com',)
        message.subject = 'subject'
        date = time.mktime((2010, 5, 12, 2, 42, 0, 0, 0, -1))
        setattr(message, 'x-postoffice-date', '%d' % date)
        info = mailin.crackHeaders(message)
        self.assertEqual(info['date'], datetime.datetime(2010, 5, 12, 2, 42))

    def test_crackHeaders_with_date_from_date_header(self):
        import datetime
        from email.utils import formatdate
        from karl.testing import DummyUsers
        import time
        context = self._makeRoot()
        context.users = DummyUsers()
        profile = self._makeContext()
        profile.__name__ = 'extant'
        by_email = {'extant@example.com': profile}
        pf = context['profiles'] = self._makeContext()
        pf.getProfileByEmail = lambda email: by_email.get(email)
        cf = context['communities'] = self._makeContext()
        community = cf['testing'] = self._makeContext()
        tool = community['default'] = self._makeContext()
        mailin = self._makeOne(context)
        mailin.default_tool = 'default'
        message = DummyMessage()
        message.to = ('testing@example.com',)
        message.from_ = ('extant@example.com',)
        message.subject = 'subject'
        date = time.mktime((2010, 5, 12, 2, 42, 0, 0, 0, -1))
        message.date = formatdate(date)
        info = mailin.crackHeaders(message)
        self.assertEqual(info['date'], datetime.datetime(2010, 5, 12, 2, 42))

    def test_crackHeaders_default_community_in_CC(self):
        from karl.testing import DummyUsers
        context = self._makeRoot()
        context.users = DummyUsers()
        profile = self._makeContext()
        profile.__name__ = 'extant'
        by_email = {'extant@example.com': profile}
        pf = context['profiles'] = self._makeContext()
        pf.getProfileByEmail = lambda email: by_email.get(email)
        cf = context['communities'] = self._makeContext()
        community = cf['testing'] = self._makeContext()
        tool = community['default'] = self._makeContext()
        mailin = self._makeOne(context)
        mailin.default_tool = 'default'
        message = DummyMessage()
        message.to = ('phreddy@example.com',)
        message.cc = ('testing@example.com',)
        message.from_ = ('extant@example.com',)
        message.subject = 'subject'

        info = mailin.crackHeaders(message)
        self.failIf(info.get('error'))
        self.assertEqual(info['author'], 'extant')
        self.assertEqual(info['subject'], 'subject')
        targets = info['targets']
        self.assertEqual(len(targets), 1)
        info = targets[0]
        self.assertEqual(info['community'], 'testing')
        self.assertEqual(info['tool'], 'default')
        self.assertEqual(info['in_reply_to'], None)

    def test_crackHeaders_permission_denied(self):
        from karl.testing import registerDummySecurityPolicy
        registerDummySecurityPolicy('someuser', permissive=False)
        from karl.testing import DummyUsers
        context = self._makeRoot()
        context.users = DummyUsers()
        profile = self._makeContext()
        profile.__name__ = 'extant'
        by_email = {'extant@example.com': profile}
        pf = context['profiles'] = self._makeContext()
        pf.getProfileByEmail = lambda email: by_email.get(email)
        cf = context['communities'] = self._makeContext()
        community = cf['testing'] = self._makeContext()
        tool = community['default'] = self._makeContext()
        mailin = self._makeOne(context)
        mailin.default_tool = 'default'
        message = DummyMessage()
        message.to = ('testing@example.com',)
        message.from_ = ('extant@example.com',)
        message.subject = 'subject'

        info = mailin.crackHeaders(message)
        self.assertEqual(info['targets'][0]['error'], 'Permission Denied')

    def test_crackPayload_empty(self):
        mailin = self._makeOne()
        message = DummyMessage()

        text, attachments = mailin.crackPayload(message)

        self.failUnless('not found' in text)
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
        from karl.testing import registerUtility
        from karl.utilities.interfaces import IMailinTextScrubber
        _called_with = []
        def _fooScrubber(text, text_mimetype=None, is_reply=False):
            _called_with.append((text, text_mimetype, is_reply))
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
        self.assertEqual(_called_with[0][2], False)

    def test_crackPayload_single_with_scrubber_is_reply(self):
        from karl.testing import registerUtility
        from karl.utilities.interfaces import IMailinTextScrubber
        _called_with = []
        def _fooScrubber(text, text_mimetype=None, is_reply=False):
            _called_with.append((text, text_mimetype, is_reply))
            return text.upper()
        registerUtility(_fooScrubber, IMailinTextScrubber, 'foo')
        mailin = self._makeOne()
        mailin.text_scrubber = 'foo'
        message = DummyMessage()
        message.payload = 'payload'
        message.content_type = 'text/plain'
        setattr(message, 'in-reply-to', 'foo')

        text, attachments = mailin.crackPayload(message)

        self.assertEqual(text, u'PAYLOAD')
        self.assertEqual(len(attachments), 0)
        self.assertEqual(len(_called_with), 1)
        self.assertEqual(_called_with[0][0], 'payload')
        self.assertEqual(_called_with[0][1], 'text/plain')
        self.assertEqual(_called_with[0][2], True)

    def test_crackPayload_single_encoded(self):
        mailin = self._makeOne()
        message = DummyMessage()
        message.payload = 'payload'
        message.content_type = 'text/plain'
        message.charset = 'rot13'

        text, attachments = mailin.crackPayload(message)

        self.assertEqual(text, u'cnlybnq')
        self.assertEqual(len(attachments), 0)

    def test_crackPayload_single_encoded_windows_874(self):
        mailin = self._makeOne()
        message = DummyMessage()
        message.payload = 'payload'
        message.content_type = 'text/plain'
        message.charset = 'windows-874'

        text, attachments = mailin.crackPayload(message)

        self.assertEqual(text, u'payload')
        self.assertEqual(len(attachments), 0)

    def test_crackPayload_single_says_ascii_but_is_really_utf8(self):
        mailin = self._makeOne()
        message = DummyMessage()
        message.payload = 'p\xc3\xa0yload'
        message.content_type = 'text/plain'
        message.charset = 'ASCII'

        text, attachments = mailin.crackPayload(message)

        self.assertEqual(text, u'p\xe0yload')
        self.assertEqual(len(attachments), 0)

    def test_crackPayload_single_bad_encoding(self):
        mailin = self._makeOne()
        message = DummyMessage()
        message.payload = 'Atbild\xe7\xf0u jums p\xe7c atgrie\xf0an\xe2s'
        message.content_type = 'text/plain'
        message.charset = 'windows-foo'

        text, attachments = mailin.crackPayload(message)

        self.assertEqual(text, u'Atbild\xe7\xf0u jums p\xe7c atgrie\xf0an\xe2s')
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

        self.failUnless('not found' in text)
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
        from karl.testing import registerUtility
        from karl.utilities.interfaces import IMailinTextScrubber
        _called_with = []
        def _fooScrubber(text, text_mimetype=None, is_reply=False):
            _called_with.append((text, text_mimetype, is_reply))
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
        self.assertEqual(_called_with[0][2], False)

    def test_crackPayload_w_multiple_text(self):
        from karl.testing import registerUtility
        from karl.utilities.interfaces import IMailinTextScrubber
        _called_with = []
        def _fooScrubber(text, text_mimetype=None, is_reply=False):
            _called_with.append((text, text_mimetype, is_reply))
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
        textpart2 = DummyMessage()
        textpart2.payload = 'howdy folks.\n'
        textpart2.charset = 'ascii'
        textpart2.content_type = 'text/plain'
        message.payload = (textpart, filepart, textpart2)

        text, attachments = mailin.crackPayload(message)

        self.assertEqual(text, u'CNLYBNQ\n\nHOWDY FOLKS.\n')
        self.assertEqual(len(attachments), 1)
        filename, mimetype, data = attachments[0]
        self.assertEqual(filename, 'file1.bin')
        self.assertEqual(mimetype, 'application/octet-stream')
        self.assertEqual(data, '0123456789ABCDEF')
        self.assertEqual(len(_called_with), 1)
        self.assertEqual(_called_with[0][0], 'cnlybnq\n\nhowdy folks.\n')
        self.assertEqual(_called_with[0][1], 'text/plain')
        self.assertEqual(_called_with[0][2], False)

    def test_crackPayload_w_forwarded_message(self):
        from karl.testing import registerUtility
        from karl.utilities.interfaces import IMailinTextScrubber
        _called_with = []
        def _fooScrubber(text, text_mimetype=None, is_reply=False):
            _called_with.append((text, text_mimetype, is_reply))
            return text.upper()
        registerUtility(_fooScrubber, IMailinTextScrubber, 'foo')
        mailin = self._makeOne()
        mailin.text_scrubber = 'foo'
        message = DummyMessage()
        filepart = DummyMessage()
        filepart.filename = 'file1.bin'
        filepart.payload = '0123456789ABCDEF'
        filepart.content_type = 'application/octet-stream'
        forwarded = DummyMessage()
        forwarded.payload = None
        forwarded.filename = "Re: prune script testing."
        forwarded.content_type='message/rfc822; name="Re: prune script..."'
        textpart = DummyMessage()
        textpart.payload = 'payload'
        textpart.charset = 'rot13'
        textpart.content_type = 'text/plain'
        textpart2 = DummyMessage()
        textpart2.payload = 'howdy folks.\n'
        textpart2.charset = 'ascii'
        textpart2.content_type = 'text/plain'
        message.payload = (textpart, forwarded, filepart, textpart2)

        text, attachments = mailin.crackPayload(message)

        self.assertEqual(text, u'CNLYBNQ\n\nHOWDY FOLKS.\n')
        self.assertEqual(len(attachments), 1)
        filename, mimetype, data = attachments[0]
        self.assertEqual(filename, 'file1.bin')
        self.assertEqual(mimetype, 'application/octet-stream')
        self.assertEqual(data, '0123456789ABCDEF')
        self.assertEqual(len(_called_with), 1)
        self.assertEqual(_called_with[0][0], 'cnlybnq\n\nhowdy folks.\n')
        self.assertEqual(_called_with[0][1], 'text/plain')
        self.assertEqual(_called_with[0][2], False)


class DummyMessage:
    to = None
    from_ = None
    subject = None
    payload = ()
    content_type = None
    charset = None
    filename = None
    date = None

    def _munge(self, name):
        name = name.lower()
        if name == 'from':
            name = 'from_'
        if name == 'x-original-to':
            name = 'x_original_to'
        return name

    def get_all(self, name, failobj=None):
        name = self._munge(name)
        return getattr(self, name, failobj)

    def __getitem__(self, key):
        key = self._munge(key)
        return getattr(self, key)

    def get(self, key, default=None):
        key = self._munge(key)
        return getattr(self, key, default)

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
