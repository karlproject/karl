# Copyright (C) 2008-2009 Open Society Institute
#               Thomas Moroz: tmoroz@sorosny.org
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License Version 2 as published
# by the Free Software Foundation.  You may not use, modify or distribute
# this program under any other version of the GNU General Public License.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; withoutg even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import unittest
from zope.testing.cleanup import cleanUp

from repoze.bfg import testing
from karl import testing as karltesting

class ShowMembersViewTests(unittest.TestCase):

    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.members import show_members_view
        return show_members_view(context, request)

    def test_show_members(self):
        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch
        context = testing.DummyModel()
        context.member_names = ['a']
        context.moderator_names = ['b']
        profiles = testing.DummyModel()
        profiles['a'] = karltesting.DummyProfile()
        profiles['b'] = karltesting.DummyProfile()
        context['profiles'] = profiles
        d = {1:profiles['a'], 2:profiles['b']}
        searchkw = {}
        def resolver(docid):
            return d.get(docid)
        def dummy_catalog_search(context):
            def search(**kw):
                searchkw.update(kw)
                return 2, [1,2], resolver
            return search
        testing.registerAdapter(dummy_catalog_search, (Interface),
                                ICatalogSearch)
        from karl.models.interfaces import ICommunity
        from zope.interface import directlyProvides
        directlyProvides(context, ICommunity)
        request = testing.DummyRequest(params={'hide_pictures':True})
        renderer = testing.registerDummyRenderer('templates/show_members.pt')
        self._callFUT(context, request)
        actions = [('Manage Members', 'manage.html'),
                   ('Add Existing', 'add_existing.html'),
                   ('Invite New', 'invite_new.html')]
        self.assertEqual(renderer.actions, actions)
        self.assertEqual(len(renderer.members), 2)
        self.assertEqual(len(renderer.moderators), 1)
        self.assertEqual(renderer.hide_pictures, True)
        self.assertEqual(len(renderer.submenu), 2)
        self.assertEqual(renderer.submenu[0]['make_link'], True)
        self.assertEqual(renderer.submenu[1]['make_link'], False)
        self.assertEqual(searchkw['sort_index'], 'lastfirst')

class AddExistingUserFormControllerTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _makeOne(self, context, request):
        from karl.views.members import AddExistingUserFormController
        return AddExistingUserFormController(context, request)

    def _getContext(self):
        context = testing.DummyModel()
        from karl.models.interfaces import ICommunity
        from zope.interface import directlyProvides
        directlyProvides(context, ICommunity)
        context.users = karltesting.DummyUsers()
        context.title = 'thetitle'
        context.description = 'description'
        context.members_group_name = 'members'
        context['profiles'] = testing.DummyModel()
        admin = testing.DummyModel()
        admin.email = 'admin@example.com'
        context['profiles']['admin'] = admin

        return context

    def test_handle_cancel(self):
        context = testing.DummyModel()
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        response = controller.handle_cancel()
        self.assertEqual(response.location, 'http://example.com/')

    def test__call__(self):
        context = self._getContext()
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        info = controller()
        actions = [('Manage Members', 'manage.html'),
                   ('Add Existing', 'add_existing.html'),
                   ('Invite New', 'invite_new.html')]
        self.assertEqual(info['actions'], actions)
        self.failUnless('page_title' in info)
        self.failUnless('page_description' in info)

    def test___call__with_userid_get(self):
        from repoze.sendmail.interfaces import IMailDelivery
        request = testing.DummyRequest({"user_id": "admin"})
        context = self._getContext()
        mailer = karltesting.DummyMailer()
        testing.registerUtility(mailer, IMailDelivery)
        controller = self._makeOne(context, request)
        response = controller()
        self.assertEqual(context.users.added_groups, [('admin','members')])
        self.assertEqual(mailer[0].mto[0], 'admin@example.com')
        self.failUnless(
            response.location.startswith('http://example.com/manage.html'))

    def test_handle_submit_badprofile(self):
        from repoze.bfg.formish import ValidationError
        request = testing.DummyRequest()
        context = self._getContext()
        controller = self._makeOne(context, request)
        converted = {'users':('admin', 'nyc99'), 'text':'some text'}
        self.assertRaises(ValidationError, controller.handle_submit, converted)

    def test_handle_submit_success(self):
        from repoze.sendmail.interfaces import IMailDelivery
        request = testing.DummyRequest()
        context = self._getContext()
        mailer = karltesting.DummyMailer()
        testing.registerUtility(mailer, IMailDelivery)
        controller = self._makeOne(context, request)
        converted = {'users': (u'admin',), 'text':'some_text'}
        response = controller.handle_submit(converted)
        self.assertEqual(context.users.added_groups, [('admin','members')])
        self.assertEqual(mailer[0].mto[0], 'admin@example.com')
        self.failUnless(
            response.location.startswith('http://example.com/manage.html'))

class AcceptInvitationFormControllerTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _makeContext(self):
        context = testing.DummyModel(sessions=DummySessions())
        return context

    def _makeRequest(self):
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        return request
    
    def _makeOne(self, context, request):
        from karl.views.members import AcceptInvitationFormController
        return AcceptInvitationFormController(context, request)

    def test_handle_cancel(self):
        context = self._makeContext()
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        response = controller.handle_cancel()
        self.assertEqual(response.location, 'http://example.com/')

    def test__call__(self):
        from karl.models.interfaces import ICommunity
        from zope.interface import directlyProvides
        context = self._makeContext()
        request = self._makeRequest()
        directlyProvides(context, ICommunity)
        context.title = 'The Community'
        controller = self._makeOne(context, request)
        info = controller()
        self.failUnless('page_title' in info)
        self.failUnless('page_description' in info)
        self.failUnless('api' in info)

    def test_form_fields(self):
        context = self._makeContext()
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        fields = controller.form_fields()
        self.failUnless(fields)

    def test_form_widgets(self):
        context = self._makeContext()
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        widgets = controller.form_widgets(None)
        self.failUnless(widgets)

    def test_handle_submit_password_mismatch(self):
        from repoze.bfg.formish import ValidationError
        context = self._makeContext()
        request = self._makeRequest()
        controller = self._makeOne(context, request)
        converted = {'password':'1', 'password_confirm':'2'}
        self.assertRaises(ValidationError, controller.handle_submit, converted)

    def test_handle_submit_username_exists(self):
        from repoze.bfg.formish import ValidationError
        context = self._makeContext()
        request = self._makeRequest()
        profiles = testing.DummyModel()
        profiles['a'] = karltesting.DummyProfile()
        context['profiles'] = profiles
        controller = self._makeOne(context, request)
        converted = {'password':'1', 'password_confirm':'1', 'username':'a'}
        self.assertRaises(ValidationError, controller.handle_submit, converted)

    def test_handle_submit_success(self):
        from karl.models.interfaces import IProfile
        from repoze.lemonade.testing import registerContentFactory
        from repoze.sendmail.interfaces import IMailDelivery
        from repoze.workflow.testing import registerDummyWorkflow
        from karl.models.interfaces import ICommunity
        from zope.interface import directlyProvides
        workflow = registerDummyWorkflow('security')
        mailer = karltesting.DummyMailer()
        testing.registerUtility(mailer, IMailDelivery)
        registerContentFactory(DummyContent, IProfile)
        class DummyWhoPlugin(object):
            def remember(self, environ, identity):
                self.identity = identity
                return []
        plugin = DummyWhoPlugin()
        whoplugins = {'auth_tkt':plugin}
        request = self._makeRequest()
        request.environ['repoze.who.plugins'] = whoplugins
        community = testing.DummyModel()
        profiles = testing.DummyModel()
        community['profiles'] = profiles
        community.users = karltesting.DummyUsers()
        community.members_group_name = 'community:members'
        directlyProvides(community, ICommunity)
        context = self._makeContext()
        community['invite'] = context
        community.title = 'Community'
        community.description = 'Community'
        community.sessions = DummySessions()
        context.email = 'a@example.com'
        controller = self._makeOne(context, request)
        converted = {'password':'1', 'password_confirm':'1',
                     'username':'username',
                     'firstname':'firstname', 'lastname':'lastname',
                     'phone':'phone', 'extension':'extension',
                     'department':'department', 'position':'position',
                     'organization':'organization', 'location':'location',
                     'country':'country', 'website':'website',
                     'languages':'languages',
                     }
        response = controller.handle_submit(converted)
        self.assertEqual(response.location,
                         'http://example.com/?status_message=Welcome%21')
        self.assertEqual(community.users.added,
                         ('username', 'username', '1', ['community:members']))
        self.assertEqual(plugin.identity, {'repoze.who.userid':'username'})
        profiles = community['profiles']
        self.failUnless('username' in profiles)
        self.assertEqual(workflow.initialized,[profiles['username']])
        self.failIf('invite' in community)
        self.assertEqual(len(mailer), 1)

class InviteNewUsersFormControllerTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from karl.views.members import InviteNewUsersFormController
        return InviteNewUsersFormController

    def _makeOne(self, context, request):
        return self._getTargetClass()(context, request)

    def _registerMailer(self):
        from repoze.sendmail.interfaces import IMailDelivery
        mailer = karltesting.DummyMailer()
        testing.registerUtility(mailer, IMailDelivery)
        return mailer

    def _makeCommunity(self):
        from karl.models.interfaces import ICommunity
        from zope.interface import directlyProvides
        community = testing.DummyModel()
        community.member_names = set(['a'])
        community.moderator_names = set(['b', 'c'])
        users = karltesting.DummyUsers(community)
        community.users = users
        directlyProvides(community, ICommunity)
        community.moderators_group_name = 'group:community:moderators'
        community.members_group_name = 'group:community:members'
        community.title = 'community'
        community.description = 'description'
        return community

    def test_form_fields(self):
        context = self._makeCommunity()
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        fields = controller.form_fields()
        self.assertEqual(len(fields), 2)

    def test_form_widgets(self):
        context = self._makeCommunity()
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        widgets = controller.form_widgets(None)
        self.assertEqual(type(widgets), dict)

    def test_call(self):
        context = self._makeCommunity()
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        result = controller()
        self.failUnless('api' in result)
        self.failUnless('actions' in result)
        self.failUnless('page_title' in result)
        self.failUnless('page_description' in result)

    def test_handle_cancel(self):
        context = self._makeCommunity()
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        result = controller.handle_cancel()
        self.assertEqual(result.location, 'http://example.com/')
        
    def test_handle_submit_new_to_karl(self):
        from repoze.lemonade.testing import registerContentFactory
        from karl.models.interfaces import IInvitation
        from karl.utilities.interfaces import IRandomId
        request = testing.DummyRequest()
        context = self._makeCommunity()
        mailer = self._registerMailer()
        registerCatalogSearch()
        def nonrandom(size=6):
            return 'A' * size
        testing.registerUtility(nonrandom, IRandomId)
        registerContentFactory(DummyInvitation, IInvitation)
        controller = self._makeOne(context, request)
        converted = {
            'email_addresses': [u'yo@plope.com'],
            'text': u'some text',
            }

        response = controller.handle_submit(converted)
        self.assertEqual(response.location,
          'http://example.com/manage.html?status_message=One+user+invited.++'
                         )
        invitation = context['A'*6]
        self.assertEqual(invitation.email, 'yo@plope.com')
        self.assertEqual(1, len(mailer))
        self.assertEqual(mailer[0].mto, [u"yo@plope.com",])

    def test_handle_submit_already_in_karl(self):
        from repoze.lemonade.testing import registerContentFactory
        from karl.models.interfaces import IInvitation
        from karl.utilities.interfaces import IRandomId
        request = testing.DummyRequest()
        context = self._makeCommunity()
        mailer = self._registerMailer()
        registerCatalogSearch()
        profile = karltesting.DummyProfile()
        profile.__name__ = 'd'
        registerCatalogSearch(results={'email=d@x.org': [profile,]})
        def nonrandom(size=6):
            return 'A' * size
        testing.registerUtility(nonrandom, IRandomId)
        registerContentFactory(DummyInvitation, IInvitation)
        controller = self._makeOne(context, request)
        converted = {
            'email_addresses': [u'd@x.org'],
            'text': u'some text',
            }
        response = controller.handle_submit(converted)
        self.assertEqual(response.location,
          'http://example.com/manage.html?status_message=One+existing+Karl+user+added+to+community.++'
                         )
        self.failIf('A'*6 in context)
        self.assertEqual(context.users.added_groups,
                         [('d', 'group:community:members')])

    def test_handle_submit_already_in_community(self):
        from repoze.lemonade.testing import registerContentFactory
        from karl.models.interfaces import IInvitation
        from karl.utilities.interfaces import IRandomId
        request = testing.DummyRequest()
        context = self._makeCommunity()
        mailer = self._registerMailer()
        registerCatalogSearch()
        profile = karltesting.DummyProfile()
        profile.__name__ = 'a'
        registerCatalogSearch(results={'email=a@x.org': [profile,]})
        def nonrandom(size=6):
            return 'A' * size
        testing.registerUtility(nonrandom, IRandomId)
        registerContentFactory(DummyInvitation, IInvitation)
        controller = self._makeOne(context, request)
        converted = {
            'email_addresses': [u'a@x.org'],
            'text': u'some text',
            }
        response = controller.handle_submit(converted)
        self.assertEqual(response.location,
          'http://example.com/manage.html?status_message=One+user+already+member.'
                         )
        self.failIf('A'*6 in context)
        self.assertEqual(context.users.added_groups, [])
        

class ManageMembersFormControllerTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from karl.views.members import ManageMembersFormController
        return ManageMembersFormController

    def _makeOne(self, context, request):
        return self._getTargetClass()(context, request)

    def _registerMailer(self):
        from repoze.sendmail.interfaces import IMailDelivery
        mailer = karltesting.DummyMailer()
        testing.registerUtility(mailer, IMailDelivery)
        return mailer

    def _makeCommunity(self):
        from karl.models.interfaces import ICommunity
        from karl.models.interfaces import IInvitation
        from zope.interface import directlyProvides
        community = testing.DummyModel()
        community.member_names = set(['a'])
        community.moderator_names = set(['b', 'c'])
        site = testing.DummyModel()
        site['communities'] = testing.DummyModel()
        site['communities']['community'] = community
        profiles = testing.DummyModel()
        profiles['a'] = karltesting.DummyProfile()
        profiles['b'] = karltesting.DummyProfile()
        profiles['c'] = karltesting.DummyProfile()
        invitation = testing.DummyModel(email='foo@example.com',
                                        message='message')
        directlyProvides(invitation, IInvitation)
        community['invitation'] = invitation
        site['profiles'] = profiles
        users = karltesting.DummyUsers(community)
        site.users = users
        directlyProvides(community, ICommunity)
        community.moderators_group_name = 'moderators'
        community.members_group_name = 'members'
        return community

    def test_form_defaults(self):
        context = self._makeCommunity()
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)

        defaults = controller.form_defaults()
        members = defaults['members']
        self.assertEqual(len(members), 4)

        self.assertEqual(members[0]['member'], True)
        self.assertEqual(members[0]['name'], 'c')
        self.assertEqual(members[0]['moderator'], True)

        self.assertEqual(members[1]['member'], True)
        self.assertEqual(members[1]['name'], 'b')
        self.assertEqual(members[1]['moderator'], True)

        self.assertEqual(members[2]['member'], True)
        self.assertEqual(members[2]['name'], 'a')
        self.assertEqual(members[2]['moderator'], False)

        self.assertEqual(members[3]['member'], False)
        self.assertEqual(members[3]['name'], 'invitation')
        self.assertEqual(members[3]['moderator'], False)

    def test_form_fields(self):
        context = self._makeCommunity()
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        fields = controller.form_fields()
        self.assertEqual(len(fields), 1)
        self.assertEqual(fields[0][1].title, '')

    def test_form_widgets(self):
        context = self._makeCommunity()
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        widgets = controller.form_widgets(None)
        self.assertEqual(type(widgets), dict)

    def test_call(self):
        context = self._makeCommunity()
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        result = controller()
        self.failUnless('api' in result)
        self.failUnless('actions' in result)
        self.failUnless('page_title' in result)

    def test_handle_cancel(self):
        context = self._makeCommunity()
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        result = controller.handle_cancel()
        self.assertEqual(result.location,
                         'http://example.com/communities/community/')
        
    def test_handle_submit_remove_sole_moderator(self):
        from repoze.bfg.formish import ValidationError
        context = self._makeCommunity()
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        converted = {'members':[
            {'remove':True, 'name':'b', 'resend':False,
             'moderator':False, 'title':'buz'},
            {'remove':True, 'name':'c', 'resend':False,
             'moderator':False, 'title':'buz'},
            ],
                     }
        self.assertRaises(ValidationError, controller.handle_submit, converted)

    def test_handle_submit_deop_sole_moderator(self):
        from repoze.bfg.formish import ValidationError
        context = self._makeCommunity()
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        converted = {'members':[
            {'remove':False, 'name':'b', 'resend':False,
             'moderator':False, 'title':'buz'},
            {'remove':False, 'name':'c', 'resend':False,
             'moderator':False, 'title':'buz'},
            ],
                     }
        self.assertRaises(ValidationError, controller.handle_submit, converted)

    def test_handle_submit_remove_member(self):
        context = self._makeCommunity()
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        converted = {'members':[{'remove':True, 'name':'a', 'resend':False,
                                 'moderator':False, 'title':'buz'}]}
        mailer = self._registerMailer()
        response = controller.handle_submit(converted)
        site = context.__parent__.__parent__
        users = site.users
        self.assertEqual(users.removed_groups, [(u'a', 'members')])
        self.assertEqual(len(mailer), 0)
        self.assertEqual(response.location,
                         'http://example.com/communities/community/'
                         'manage.html?status_message='
                         'Membership+information+changed%3A+'
                         'Removed+member+buz')

    def test_handle_submit_remove_invitation(self):
        context = self._makeCommunity()
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        converted = {'members':[{'remove':True, 'name':'invitation',
                                 'resend':False, 'moderator':False,
                                 'title':'buz'}]}
        mailer = self._registerMailer()
        response = controller.handle_submit(converted)
        site = context.__parent__.__parent__
        users = site.users
        self.assertEqual(len(mailer), 0)
        self.failIf('invitation' in context)
        self.assertEqual(response.location,
                         'http://example.com/communities/community/'
                         'manage.html?status_message='
                         'Membership+information+changed%3A+'
                         'Removed+invitation+buz')

    def test_handle_submit_remove_moderator(self):
        context = self._makeCommunity()
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        converted = {'members':[{'remove':True, 'name':'b', 'resend':False,
                                 'moderator':False, 'title':'buz'}]}
        mailer = self._registerMailer()
        response = controller.handle_submit(converted)
        site = context.__parent__.__parent__
        users = site.users
        self.assertEqual(users.removed_groups, [(u'b', 'moderators')])
        self.assertEqual(len(mailer), 0)
        self.assertEqual(response.location,
                         'http://example.com/communities/community/'
                         'manage.html?status_message='
                         'Membership+information+changed%3A+'
                         'Removed+moderator+buz')

    def test_handle_submit_resend(self):
        context = self._makeCommunity()
        context.title = 'community'
        context.description = 'description'
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        converted = {'members':[{'remove':False, 'name':'invitation',
                                 'resend':True, 'moderator':False,
                                 'title':'buz'}]}
        mailer = self._registerMailer()
        response = controller.handle_submit(converted)
        self.assertEqual(len(mailer), 1)
        self.assertEqual(response.location,
                         'http://example.com/communities/community/'
                         'manage.html?status_message='
                         'Membership+information+changed%3A+'
                         'Resent+invitation+to+buz')

    def test_handle_submit_add_moderator(self):
        context = self._makeCommunity()
        context.title = 'community'
        context.description = 'description'
        request = testing.DummyRequest()
        controller = self._makeOne(context, request)
        converted = {'members':[{'remove':False, 'name':'a',
                                 'resend':False, 'moderator':True,
                                 'title':'buz'}]}
        mailer = self._registerMailer()
        response = controller.handle_submit(converted)
        self.assertEqual(len(mailer), 0)
        self.assertEqual(response.location,
                         'http://example.com/communities/community/'
                         'manage.html?status_message='
                         'Membership+information+changed%3A+'
                         'buz+is+now+a+moderator')

class TestJqueryMemberSearchView(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.members import jquery_member_search_view
        return jquery_member_search_view(context, request)

    def test_it(self):
        from zope.interface import Interface
        from zope.interface import directlyProvides
        from karl.models.interfaces import ICatalogSearch
        from karl.models.interfaces import ICommunity
        context = testing.DummyModel()
        directlyProvides(context, ICommunity)
        context.member_names = set('a',)
        context.moderator_names = set()
        request = testing.DummyRequest(params={'val':'a'})
        profiles = testing.DummyModel()
        profile_1 = karltesting.DummyProfile(__name__='a')
        profile_2 = karltesting.DummyProfile(__name__='b')
        profile_3 = karltesting.DummyProfile(__name__='c')
        def resolver(docid):
            d = {1:profile_1, 2:profile_2, 3:profile_3}
            return d.get(docid)
        def dummy_catalog_search(context):
            def search(**kw):
                return 3, [1,2,3], resolver
            return search
        testing.registerAdapter(dummy_catalog_search, (Interface),
                                ICatalogSearch)
        response = self._callFUT(context, request)
        self.assertEqual(response.body, '[{"text": "firstname lastname", "id": "b"}, {"text": "firstname lastname", "id": "c"}]')

class TestAcceptInvitationPhotoView(unittest.TestCase):
    def _callFUT(self, context, request):
        from karl.views.members import accept_invitation_photo_view
        return accept_invitation_photo_view(context, request)

    def test_it(self):
        request = testing.DummyRequest()
        request.environ['repoze.browserid'] = '1'
        request.subpath = ('a',)
        sessions = DummySessions()
        class DummyBlob:
            def open(self, mode):
                return ('abc',)
        sessions['1'] = {'accept-invitation':
                         {'a':([('a', '1')],None, DummyBlob())}
                         }
        context = testing.DummyModel(sessions=sessions)
        response = self._callFUT(context, request)
        self.assertEqual(response.headerlist, [('a', '1')])
        self.assertEqual(response.app_iter, ('abc',))

class DummyMembers(testing.DummyModel):
    def __init__(self):
        testing.DummyModel.__init__(self)
        self.__parent__ = karltesting.DummyCommunity()
        self.__name__ = 'members'

class DummyInvitation:
    def __init__(self, email, message):
        self.email = email
        self.message = message

class DummyContent:
    def __init__(self, **kw):
        for key,value in kw.items():
            setattr(self, key, value)

def dummy_search(results):
    class DummySearchAdapter:
        def __init__(self, context, request=None):
            self.context = context
            self.request = request

        def __call__(self, **kw):
            search = []
            for k,v in kw.items():
                key = '%s=%s' % (k,v)
                if key in results:
                    search.extend(results[key])

            return len(search), search, lambda x: x

    return DummySearchAdapter

def registerCatalogSearch(results={}):
    from repoze.bfg.testing import registerAdapter
    from zope.interface import Interface
    from karl.models.interfaces import ICatalogSearch
    registerAdapter(dummy_search(results), (Interface,), ICatalogSearch)

class DummySessions(dict):
    def get(self, name, default=None):
        if name not in self:
            self[name] = {}
        return self[name]
