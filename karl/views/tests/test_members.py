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

class AddExistingUserViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.members import add_existing_user_view
        return add_existing_user_view(context, request)

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

    def test_cancelled(self):
        context = testing.DummyModel()
        request = testing.DummyRequest(params={'form.cancel':'1'})
        response = self._callFUT(context, request)
        self.assertEqual(response.location, 'http://example.com/')

    def test_notsubmitted(self):
        context = self._getContext()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
            'templates/add_existing_user.pt')
        renderer2 = testing.registerDummyRenderer(
            'templates/form_add_existing_user.pt',
            renderer=StringTemplateRenderer('<form>fake</form>'))
        self._callFUT(context, request)
        actions = [('Manage Members', 'manage.html'), 
                   ('Add Existing', 'add_existing.html'), 
                   ('Invite New', 'invite_new.html')]
        self.assertEqual(renderer.actions, actions)

    def test_submitted_invalid(self):
        tn = 'templates/add_existing_user.pt'
        renderer = testing.registerDummyRenderer(tn)
        renderer2 = testing.registerDummyRenderer(
            'templates/form_add_existing_user.pt',
            renderer=StringTemplateRenderer('<form>fake</form>'))
        from webob import MultiDict
        request = testing.DummyRequest(MultiDict({'form.submitted':1}))
        context = self._getContext()
        self._callFUT(context, request)
        form = renderer.form
        self.assert_(form.cancel not in form.formdata)
        self.assert_(form.submit in form.formdata)
        self.assertEqual(renderer.form.is_valid, False)

    def test_submitted_bad_profile(self):
        # This is when a username comes in that doesn't match a
        # profile
        from repoze.sendmail.interfaces import IMailDelivery

        renderer = testing.registerDummyRenderer(
            'templates/add_existing_user.pt')
        renderer2 = testing.registerDummyRenderer(
            'templates/form_add_existing_user.pt',
            renderer=StringTemplateRenderer(
            '<form><input name="users"/><input name="text"/></form>'))
        from webob import MultiDict
        md = MultiDict({
                'form.submitted':1,
                'users': u'admin,nyc99',
                'text': u'<p>some text</p>',
                })
        request = testing.DummyRequest(md)
        context = self._getContext()
        mailer = karltesting.DummyMailer()
        testing.registerUtility(mailer, IMailDelivery)
        response = self._callFUT(context, request)
        self.failUnless('users' in renderer2.fielderrors)

    def test_submitted_success(self):
        from repoze.sendmail.interfaces import IMailDelivery

        renderer = testing.registerDummyRenderer(
            'templates/add_existing_user.pt')
        renderer2 = testing.registerDummyRenderer(
            'templates/form_add_existing_user.pt',
            renderer=StringTemplateRenderer(
            '<form><input name="users"/><input name="text"/></form>'))
        from webob import MultiDict
        md = MultiDict({
                'form.submitted':1,
                'users': u'admin',
                'text': u'<p>some text</p>',
                })
        request = testing.DummyRequest(md)
        context = self._getContext()
        mailer = karltesting.DummyMailer()
        testing.registerUtility(mailer, IMailDelivery) 
        response = self._callFUT(context, request)
        self.assertEqual(context.users.added_groups, [('admin','members')])
        self.assertEqual(mailer[0].mto[0], 'admin@example.com')
        self.failUnless(
            response.location.startswith('http://example.com/manage.html'))

    def test_submitted_via_get(self):
        from repoze.sendmail.interfaces import IMailDelivery
        request = testing.DummyRequest({"user_id": "admin"})
        request.POST = {}
        context = self._getContext()
        mailer = karltesting.DummyMailer()
        testing.registerUtility(mailer, IMailDelivery) 
        response = self._callFUT(context, request)
        self.assertEqual(context.users.added_groups, [('admin','members')])
        self.assertEqual(mailer[0].mto[0], 'admin@example.com')
        self.failUnless(
            response.location.startswith('http://example.com/manage.html'))

class AcceptInvitationViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.members import accept_invitation_view
        return accept_invitation_view(context, request)
    
    def test_cancelled(self):
        from zope.interface import directlyProvides
        from zope.interface import alsoProvides
        from karl.models.interfaces import IInvitation
        context = testing.DummyModel()
        from karl.models.interfaces import ICommunity
        directlyProvides(context, ICommunity)
        context.title = 'Some Community Title'
        context.vocabularies = {}
        alsoProvides(context, IInvitation)
        request = testing.DummyRequest(params={'form.cancel':'1'})
        response = self._callFUT(context, request)
        self.assertEqual(response.location, 'http://example.com/')

    def test_notsubmitted(self):
        from zope.interface import directlyProvides
        from zope.interface import alsoProvides
        from karl.models.interfaces import IInvitation
        context = testing.DummyModel()
        from karl.models.interfaces import ICommunity
        directlyProvides(context, ICommunity)
        context.title = 'Some Community Title'
        context.vocabularies = {'countries':[]}
        alsoProvides(context, IInvitation)
        formfields = testing.registerDummyRenderer('templates/formfields.pt')
        form = testing.registerDummyRenderer(
            'templates/form_accept_invitation.pt')
        renderer = testing.registerDummyRenderer(
            'templates/accept_invitation.pt')
        request = testing.DummyRequest()
        response = self._callFUT(context, request)
        self.failUnless(renderer.form)

    def test_submitted_failvalidation(self):
        from zope.interface import directlyProvides
        from zope.interface import alsoProvides
        from karl.models.interfaces import IInvitation
        context = testing.DummyModel()
        from karl.models.interfaces import ICommunity
        directlyProvides(context, ICommunity)
        context.title = 'Some Community Title'
        context.vocabularies = {'countries':[]}
        alsoProvides(context, IInvitation)
        formfields = testing.registerDummyRenderer(
            'templates/formfields.pt')
        form = testing.registerDummyRenderer(
            'templates/form_accept_invitation.pt')
        renderer = testing.registerDummyRenderer(
            'templates/accept_invitation.pt')
        request = testing.DummyRequest({'form.submitted':'1'})
        response = self._callFUT(context, request)
        self.failUnless(form.fielderrors)

    def test_submitted_username_exists(self):
        from zope.interface import directlyProvides
        from karl.models.interfaces import IInvitation
        context = testing.DummyModel()
        from karl.models.interfaces import ICommunity
        directlyProvides(context, ICommunity)
        context.title = 'Some Community Title'
        context['profiles'] = testing.DummyModel()
        fred = testing.DummyModel()
        context['profiles']['fred'] = fred
        directlyProvides(fred, IInvitation)
        
        context.vocabularies = {'countries':[]}
        formfields = testing.registerDummyRenderer(
            'templates/formfields.pt')
        form = testing.registerDummyRenderer(
            'templates/form_accept_invitation.pt')
        renderer = testing.registerDummyRenderer(
            'templates/accept_invitation.pt')
        request = testing.DummyRequest({'form.submitted':'1',
                                        'username':'fred',
                                        'password':'password',
                                        'password_confirm':'password',
                                        'firstname':'fred',
                                        'lastname':'flintstone',
                                        'terms_and_conditions':'1',
                                        'accept_privacy_policy':'1'})
        response = self._callFUT(fred, request)
        self.assertEqual(form.fielderrors['username'].msg,
                         'Username fred already exists')

    def test_submitted_success(self):
        from karl.models.interfaces import ICommunity
        from karl.models.interfaces import IInvitation
        from karl.models.interfaces import IProfile
        from zope.interface import directlyProvides
        from repoze.lemonade.testing import registerContentFactory
        from repoze.sendmail.interfaces import IMailDelivery
        
        registerContentFactory(DummyContent, IProfile)
        mailer = karltesting.DummyMailer()
        
        testing.registerUtility(mailer, IMailDelivery)
        context = testing.DummyModel()
        context.members_group_name = 'members'
        context.email = 'jim@example.com'
        users = karltesting.DummyUsers()
        context.users = users
        context.title = "Community Title"
        context.description = "Community Description"
        directlyProvides(context, ICommunity)
        
        context['profiles'] = testing.DummyModel()
        fred = testing.DummyModel()
        context['profiles']['fred'] = fred
        fred.email = context.email
        directlyProvides(fred, IInvitation)
        
        context.vocabularies = {'countries':[]}
        formfields = testing.registerDummyRenderer(
            'templates/formfields.pt')
        form = testing.registerDummyRenderer(
            'templates/form_accept_invitation.pt')
        renderer = testing.registerDummyRenderer(
            'templates/accept_invitation.pt')
        request = testing.DummyRequest({'form.submitted':'1',
                                        'username':'jim',
                                        'password':'password',
                                        'password_confirm':'password',
                                        'firstname':'fred',
                                        'lastname':'flintstone',
                                        'terms_and_conditions':'1',
                                        'accept_privacy_policy':'1',
                                        'phone':'',
                                        'extension':'',
                                        'organization':'',
                                        'country':'',
                                        'location':'',
                                        'department':'',
                                        'position':'',
                                        'website':'',
                                        'biography':'',
                                        'languages':'',
                                        'photo':'',
                                        })
        class DummyPlugin:
            def remember(self, environ, identity):
                self.identity = identity
                return [('a', '1')]
        plugin = DummyPlugin()
        plugins = {'auth_tkt':plugin}
        request.environ['repoze.who.plugins'] = plugins
        from karl.testing import registerSecurityWorkflow
        registerSecurityWorkflow()
        response = self._callFUT(fred, request)
        self.assertEqual(users.added, ('jim', 'jim', u'password', ['members']))
        self.failUnless('jim' in context['profiles'])
        self.failIf('fred' in context['profiles'])
        self.assertEqual(plugin.identity['repoze.who.userid'], 'jim')
        self.failUnless( ('a', '1') in response.headerlist )
        self.assertEquals(1, len(mailer))
        self.assertEquals(mailer[0].mto, ["jim@example.com",])
        
        # Make sure ISecurityWorkflow.setInitialState() called
        self.failUnless(hasattr(context['profiles']['jim'], 'initial_state'))
        
class InviteNewUserViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.members import invite_new_user_view
        return invite_new_user_view(context, request)

    def _getContext(self):
        context = testing.DummyModel()
        from karl.models.interfaces import ICommunity
        from zope.interface import directlyProvides
        directlyProvides(context, ICommunity)
        context.member_names = set()
        context.moderator_names = set()
        context.users = karltesting.DummyUsers()
        context.title = 'thetitle'
        context.description = 'description'
        context['profiles'] = testing.DummyModel()
        admin = testing.DummyModel()
        admin.email = 'admin@example.com'
        context['profiles']['admin'] = admin
        
        return context

    def test_notsubmitted(self):
        context = self._getContext()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
            'templates/invite_new_user.pt')
        self._callFUT(context, request)
        actions = [('Manage Members', 'manage.html'), 
                   ('Add Existing', 'add_existing.html'), 
                   ('Invite New', 'invite_new.html')]
        self.assertEqual(renderer.actions, actions)

    def test_cancelled(self):
        context = self._getContext()
        request = testing.DummyRequest(params={'form.cancel':'1'})
        response = self._callFUT(context, request)
        self.assertEqual(response.location, 'http://example.com/')

    def test_submitted_bademail(self): # broken
        from repoze.sendmail.interfaces import IMailDelivery
        renderer1 = testing.registerDummyRenderer(
            'templates/invite_new_user.pt')
        renderer2 = testing.registerDummyRenderer(
            'templates/formfields.pt')
        renderer3 = testing.registerDummyRenderer(
            'templates/form_invite_new_users.pt',
            renderer=StringTemplateRenderer(
            '<form><input name="email_addresses"/><input name="text"/></form>'))
        request = testing.DummyRequest({
                'form.submitted':1,
                'email_addresses': u'yo\n',
                'text': u'some text',
                })
        context = self._getContext()
        mailer = karltesting.DummyMailer()
        testing.registerUtility(mailer, IMailDelivery)
        response = self._callFUT(context, request)
        self.assertEqual(renderer1.form.is_valid, False)

    def test_submitted_ok_new_to_karl(self):
        from repoze.sendmail.interfaces import IMailDelivery
        from repoze.lemonade.testing import registerContentFactory
        from karl.models.interfaces import IInvitation
        from karl.utilities.interfaces import IRandomId
        renderer1 = testing.registerDummyRenderer(
            'templates/invite_new_user.pt')
        renderer2 = testing.registerDummyRenderer(
            'templates/formfields.pt')
        renderer3 = testing.registerDummyRenderer(
            'templates/form_invite_new_users.pt',
            renderer=StringTemplateRenderer(
            '<form><input name="email_addresses"/><input name="text"/></form>'))
        request = testing.DummyRequest({
                'form.submitted':1,
                'email_addresses': u'yo@plope.com\n',
                'text': u'some text',
                })
        context = self._getContext()
        mailer = karltesting.DummyMailer()
        testing.registerUtility(mailer, IMailDelivery)
        registerCatalogSearch()
        def nonrandom(size=6):
            return 'A' * size
        testing.registerUtility(nonrandom, IRandomId)
        registerContentFactory(DummyInvitation, IInvitation)
        response = self._callFUT(context, request)
        self.assertEqual(response.location,
          'http://example.com/manage.html?status_message=One+user+invited.++'
                         )
        invitation = context['A'*6]
        self.assertEqual(invitation.email, 'yo@plope.com')
        self.assertEqual(1, len(mailer))
        self.assertEqual(mailer[0].mto, [u"yo@plope.com",])

    def test_submitted_ok_in_karl(self):
        from repoze.sendmail.interfaces import IMailDelivery
        from repoze.lemonade.testing import registerContentFactory
        from karl.models.interfaces import IInvitation
        from karl.utilities.interfaces import IRandomId
        renderer1 = testing.registerDummyRenderer(
            'templates/invite_new_user.pt')
        renderer2 = testing.registerDummyRenderer(
            'templates/formfields.pt')
        renderer3 = testing.registerDummyRenderer(
            'templates/form_invite_new_users.pt',
            renderer=StringTemplateRenderer(
            '<form><input name="email_addresses"/><input name="text"/></form>'))
        request = testing.DummyRequest({
                'form.submitted':1,
                'email_addresses': u'a@x.org\n',
                'text': u'some text',
                })
        context = self._getContext()
        mailer = karltesting.DummyMailer()
        testing.registerUtility(mailer, IMailDelivery)
        profile = karltesting.DummyProfile()
        context['profiles']['a'] = profile
        context.members_group_name = 'group:community:members'
        registerCatalogSearch(results={'email=a@x.org': [profile,]})
        def nonrandom(size=6):
            return 'A' * size
        testing.registerUtility(nonrandom, IRandomId)
        registerContentFactory(DummyInvitation, IInvitation)
        response = self._callFUT(context, request)
        self.assertEqual(response.location,
          'http://example.com/manage.html?status_message=One+existing+Karl+user+added+to+community.++'
                         )
        self.failIf('A'*6 in context)
        self.assertEqual(context.users.added_groups, 
                         [('a', 'group:community:members')])

    def test_submitted_ok_in_community(self):
        from repoze.sendmail.interfaces import IMailDelivery
        from repoze.lemonade.testing import registerContentFactory
        from karl.models.interfaces import IInvitation
        from karl.utilities.interfaces import IRandomId
        renderer1 = testing.registerDummyRenderer(
            'templates/invite_new_user.pt')
        renderer2 = testing.registerDummyRenderer(
            'templates/formfields.pt')
        renderer3 = testing.registerDummyRenderer(
            'templates/form_invite_new_users.pt',
            renderer=StringTemplateRenderer(
            '<form><input name="email_addresses"/><input name="text"/></form>'))
        request = testing.DummyRequest({
                'form.submitted':1,
                'email_addresses': u'a@x.org\n',
                'text': u'some text',
                })
        context = self._getContext()
        mailer = karltesting.DummyMailer()
        testing.registerUtility(mailer, IMailDelivery)
        profile = karltesting.DummyProfile()
        context['profiles']['a'] = profile
        context.member_names.add('a')
        context.members_group_name = 'group:community:members'
        registerCatalogSearch(results={'email=a@x.org': [profile,]})
        def nonrandom(size=6):
            return 'A' * size
        testing.registerUtility(nonrandom, IRandomId)
        registerContentFactory(DummyInvitation, IInvitation)
        response = self._callFUT(context, request)
        self.assertEqual(response.location,
          'http://example.com/manage.html?status_message=One+user+already+member.'
                         )
        self.failIf('A'*6 in context)
        self.assertEqual(context.users.added_groups, [])
        
class ManageMembersViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.members import manage_members_view
        return manage_members_view(context, request)

    def test_cancelled(self):
        context = testing.DummyModel()
        request = testing.DummyRequest(params={'form.cancel':'1'})
        response = self._callFUT(context, request)
        self.assertEqual(response.location, 'http://example.com/')

    def test_manage_members_notsubmitted(self):
        from karl.models.interfaces import ICommunity
        from zope.interface import directlyProvides
        from karl.models.interfaces import IInvitation
        from repoze.sendmail.interfaces import IMailDelivery

        mailer = karltesting.DummyMailer()
        testing.registerUtility(mailer, IMailDelivery)

        context = karltesting.DummyCommunity()
        context.member_names = set(['a'])
        context.moderator_names = set(['b'])
        site = context.__parent__.__parent__
        profiles = testing.DummyModel()
        profiles['a'] = karltesting.DummyProfile()
        profiles['b'] = karltesting.DummyProfile()
        invitation = testing.DummyModel(email='foo@example.com')
        directlyProvides(invitation, IInvitation)
        site['profiles'] = profiles
        context['invitation'] = invitation
        directlyProvides(context, ICommunity)
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer('templates/manage_members.pt')
        self._callFUT(context, request)
        actions = [('Manage Members', 'manage.html'), 
                   ('Add Existing', 'add_existing.html'), 
                   ('Invite New', 'invite_new.html')]
        self.assertEqual(renderer.actions, actions)
        self.assertEqual(renderer.entries['moderators'],
                         [{'is_moderator': True, 'resend_info': False,
                           'id': 'b', 'remove': False, 'title': 'title',
                           'sortkey': 'lastname, firstname'}])
        self.assertEqual(renderer.entries['members'],
                         [{'is_moderator': False, 'resend_info': False,
                           'id': 'a', 'remove': False, 'title': 'title',
                           'sortkey': 'lastname, firstname'}])
        self.assertEqual(renderer.entries['invitations'],
                         [{'is_moderator': False, 'resend_info': False,
                           'id': 'invitation', 'remove': False,
                           'title': 'foo@example.com',
                           'sortkey': 'foo@example.com'}])
        self.assertEqual(0, len(mailer))
        
    def test_manage_members_remove_sole_moderator(self):
        from karl.models.interfaces import ICommunity
        from zope.interface import directlyProvides
        from karl.models.interfaces import IInvitation
        from repoze.sendmail.interfaces import IMailDelivery

        mailer = karltesting.DummyMailer()
        testing.registerUtility(mailer, IMailDelivery)

        context = karltesting.DummyCommunity()
        directlyProvides(context, ICommunity)
        context.member_names = set(['a'])
        context.moderator_names = set(['b', 'c'])
        context.title = "Some Community Title"
        context.member_names = set(['a'])
        context.moderator_names = set(['b'])
        profiles = testing.DummyModel()
        profiles['a'] = karltesting.DummyProfile()
        profiles['b'] = karltesting.DummyProfile()
        invitation = testing.DummyModel(email='foo@example.com')
        directlyProvides(invitation, IInvitation)
        site = context.__parent__.__parent__
        site['profiles'] = profiles
        users = karltesting.DummyUsers(context)
        site.users = users
        context['invitation'] = invitation
        context.moderators_group_name = 'moderators'
        context.members_group_name = 'members'
        request = testing.DummyRequest({'form.submitted':'1',
                                        'moderators-0.id':'b',
                                        'moderators-0.remove':'1'})
        renderer = testing.registerDummyRenderer('templates/manage_members.pt')
        response = self._callFUT(context, request)
        self.assertEqual(response.location, 
            'http://example.com/communities/community/manage.html?error_message=Must+leave+at+least+one+moderator+for+community.'
        )
        
    def test_manage_members_remove_second_moderator(self):
        from karl.models.interfaces import ICommunity
        from zope.interface import directlyProvides
        from karl.models.interfaces import IInvitation
        from repoze.sendmail.interfaces import IMailDelivery

        mailer = karltesting.DummyMailer()
        testing.registerUtility(mailer, IMailDelivery)

        context = karltesting.DummyCommunity()
        context.member_names = set(['a'])
        context.moderator_names = set(['b', 'c'])
        profiles = testing.DummyModel()
        profiles['a'] = karltesting.DummyProfile()
        profiles['b'] = karltesting.DummyProfile()
        profiles['c'] = karltesting.DummyProfile()
        invitation = testing.DummyModel(email='foo@example.com')
        site = context.__parent__.__parent__
        site['profiles'] = profiles
        users = karltesting.DummyUsers(context)
        site.users = users
        context['invitation'] = invitation
        directlyProvides(invitation, IInvitation)
        context.moderators_group_name = 'moderators'
        context.members_group_name = 'members'
        request = testing.DummyRequest({'form.submitted':'1',
                                        'moderators-0.id':'b',
                                        'moderators-0.remove':'1'})
        renderer = testing.registerDummyRenderer('templates/manage_members.pt')
        self._callFUT(context, request)
        # he is removed
        self.assertEqual(users.removed_groups,
                         [(u'b', 'moderators'), (u'b', 'members')] )
        self.assertEqual(1, len(mailer))
        
    def test_manage_members_remove_member(self):
        from karl.models.interfaces import ICommunity
        from zope.interface import directlyProvides
        from karl.models.interfaces import IInvitation
        from repoze.sendmail.interfaces import IMailDelivery

        mailer = karltesting.DummyMailer()
        testing.registerUtility(mailer, IMailDelivery)

        context = karltesting.DummyCommunity()
        context.member_names = set(['a'])
        context.moderator_names = set(['b', 'c'])
        profiles = testing.DummyModel()
        profiles['a'] = karltesting.DummyProfile()
        profiles['b'] = karltesting.DummyProfile()
        profiles['c'] = karltesting.DummyProfile()
        invitation = testing.DummyModel(email='foo@example.com')
        site = context.__parent__.__parent__
        site['profiles'] = profiles
        users = karltesting.DummyUsers(context)
        site.users = users
        context['invitation'] = invitation
        directlyProvides(invitation, IInvitation)
        context.moderators_group_name = 'moderators'
        context.members_group_name = 'members'
        request = testing.DummyRequest({'form.submitted':'1',
                                        'members-0.id':'a',
                                        'members-0.remove':'1'})
        renderer = testing.registerDummyRenderer('templates/manage_members.pt')
        self._callFUT(context, request)
        # he is removed
        self.assertEqual(users.removed_groups, [(u'a', 'members')])
        self.assertEqual(0, len(mailer))
        
    def test_manage_members_make_member_moderator_already_moderator(self):
        from karl.models.interfaces import ICommunity
        from zope.interface import directlyProvides
        from karl.models.interfaces import IInvitation
        from repoze.sendmail.interfaces import IMailDelivery

        mailer = karltesting.DummyMailer()
        testing.registerUtility(mailer, IMailDelivery)

        context = karltesting.DummyCommunity()
        context.member_names = set(['a'])
        context.moderator_names = set(['b', 'c'])
        profiles = testing.DummyModel()
        profiles['a'] = karltesting.DummyProfile()
        profiles['b'] = karltesting.DummyProfile()
        profiles['c'] = karltesting.DummyProfile()
        invitation = testing.DummyModel(email='foo@example.com')
        directlyProvides(invitation, IInvitation)
        site = context.__parent__.__parent__
        site['profiles'] = profiles
        users = karltesting.DummyUsers(context)
        site.users = users
        context['invitation'] = invitation
        context.moderators_group_name = 'moderators'
        context.members_group_name = 'members'
        request = testing.DummyRequest({'form.submitted':'1',
                                        'members-0.id':'b',
                                        'members-0.is_moderator':'1'})
        renderer = testing.registerDummyRenderer('templates/manage_members.pt')
        self._callFUT(context, request)
        # he already a moderator
        self.assertEqual(users.added_groups, [])
        self.assertEqual(users.removed_groups, [])
        self.assertEqual(0, len(mailer))
        
    def test_manage_members_make_member_moderator_not_already_moderator(self):
        from karl.models.interfaces import ICommunity
        from zope.interface import directlyProvides
        from karl.models.interfaces import IInvitation
        from repoze.sendmail.interfaces import IMailDelivery

        mailer = karltesting.DummyMailer()
        testing.registerUtility(mailer, IMailDelivery)

        context = karltesting.DummyCommunity()
        context.member_names = set(['a'])
        context.moderator_names = set(['b', 'c'])
        profiles = testing.DummyModel()
        profiles['a'] = karltesting.DummyProfile()
        profiles['b'] = karltesting.DummyProfile()
        profiles['c'] = karltesting.DummyProfile()
        invitation = testing.DummyModel(email='foo@example.com')
        directlyProvides(invitation, IInvitation)
        site = context.__parent__.__parent__
        site['profiles'] = profiles
        users = karltesting.DummyUsers(context)
        site.users = users
        context['invitation'] = invitation
        context.moderators_group_name = 'moderators'
        context.members_group_name = 'members'
        request = testing.DummyRequest({'form.submitted':'1',
                                        'members-0.id':'a',
                                        'members-0.is_moderator':'1'})
        renderer = testing.registerDummyRenderer('templates/manage_members.pt')
        self._callFUT(context, request)
        # he is now a moderator
        self.assertEqual(users.added_groups, [(u'a', 'moderators')])
        self.assertEqual(1, len(mailer))
        
    def test_manage_members_make_member_remove_moderator_from_member(self):
        from karl.models.interfaces import ICommunity
        from zope.interface import directlyProvides
        from karl.models.interfaces import IInvitation
        from repoze.sendmail.interfaces import IMailDelivery

        mailer = karltesting.DummyMailer()
        testing.registerUtility(mailer, IMailDelivery)

        context = karltesting.DummyCommunity()
        context.member_names = set(['a'])
        context.moderator_names = set(['b', 'c'])
        profiles = testing.DummyModel()
        profiles['a'] = karltesting.DummyProfile()
        profiles['b'] = karltesting.DummyProfile()
        profiles['c'] = karltesting.DummyProfile()
        invitation = testing.DummyModel(email='foo@example.com')
        directlyProvides(invitation, IInvitation)
        site = context.__parent__.__parent__
        site['profiles'] = profiles
        users = karltesting.DummyUsers(context)
        site.users = users
        context['invitation'] = invitation
        context.moderators_group_name = 'moderators'
        context.members_group_name = 'members'
        request = testing.DummyRequest({'form.submitted':'1',
                                        'moderators-0.id':'b',
                                        'mmoderators-0.is_moderator':''})
        renderer = testing.registerDummyRenderer('templates/manage_members.pt')
        self._callFUT(context, request)
        # he is no longer a moderator
        self.assertEqual(users.removed_groups, [(u'b', 'moderators')])
        self.assertEqual(1, len(mailer))
        
    def test_manage_members_remove_invitation(self):
        from karl.models.interfaces import ICommunity
        from karl.models.interfaces import IInvitation
        from zope.interface import directlyProvides
        context = karltesting.DummyCommunity()
        context.member_names = set()
        context.moderator_names = set()
        profiles = testing.DummyModel()
        invitation = testing.DummyModel(email='foo@example.com')
        directlyProvides(invitation, IInvitation)
        site = context.__parent__.__parent__
        site['profiles'] = profiles
        users = karltesting.DummyUsers(context)
        site.users = users
        context['invitation'] = invitation
        context.moderators_group_name = 'moderators'
        context.members_group_name = 'members'
        directlyProvides(context, ICommunity)
        request = testing.DummyRequest({'form.submitted':'1',
                                        'invitations-0.id':'invitation',
                                        'invitations-0.resend_info':'0',
                                        'invitations-0.remove':'1',
                                        })
        renderer = testing.registerDummyRenderer('templates/manage_members.pt')
        self._callFUT(context, request)
        # the invitation is removed
        self.failIf('invitation' in context)
        
    def test_manage_members_resend_invitation(self):
        from karl.models.interfaces import ICommunity
        from karl.models.interfaces import IInvitation
        from zope.interface import directlyProvides
        from repoze.sendmail.interfaces import IMailDelivery

        mailer = karltesting.DummyMailer()
        testing.registerUtility(mailer, IMailDelivery)

        context = karltesting.DummyCommunity()
        context.member_names = set(['a'])
        context.moderator_names = set(['b', 'c'])
        profiles = testing.DummyModel()
        profiles['a'] = karltesting.DummyProfile()
        profiles['b'] = karltesting.DummyProfile()
        profiles['c'] = karltesting.DummyProfile()
        invitation = testing.DummyModel(email='foo@example.com', 
                                        message='Hello there')
        directlyProvides(invitation, IInvitation)
        site = context.__parent__.__parent__
        site['profiles'] = profiles
        users = karltesting.DummyUsers(context)
        site.users = users
        context['invitation'] = invitation
        context.moderators_group_name = 'moderators'
        context.members_group_name = 'members'
        directlyProvides(context, ICommunity)
        request = testing.DummyRequest({'form.submitted':'1',
                                        'invitations-0.id':'invitation',
                                        'invitations-0.resend_info':'1',
                                        })
        renderer = testing.registerDummyRenderer('templates/manage_members.pt')
        self._callFUT(context, request)
        
        self.assertEqual(1, len(mailer))
        self.assertEqual(['foo@example.com',], mailer[0].mto)

    def test_manage_members_remove_blocks_resend_invitation(self):
        from karl.models.interfaces import ICommunity
        from karl.models.interfaces import IInvitation
        from zope.interface import directlyProvides
        from repoze.sendmail.interfaces import IMailDelivery

        mailer = karltesting.DummyMailer()
        testing.registerUtility(mailer, IMailDelivery)

        context = karltesting.DummyCommunity()
        context.member_names = set(['a'])
        context.moderator_names = set(['b', 'c'])
        profiles = testing.DummyModel()
        profiles['a'] = karltesting.DummyProfile()
        profiles['b'] = karltesting.DummyProfile()
        profiles['c'] = karltesting.DummyProfile()
        invitation = testing.DummyModel(email='foo@example.com', 
                                        message='Hello there')
        directlyProvides(invitation, IInvitation)
        site = context.__parent__.__parent__
        site['profiles'] = profiles
        users = karltesting.DummyUsers(context)
        site.users = users
        context['invitation'] = invitation
        context.moderators_group_name = 'moderators'
        context.members_group_name = 'members'
        directlyProvides(context, ICommunity)
        request = testing.DummyRequest({'form.submitted':'1',
                                        'invitations-0.id':'invitation',
                                        'invitations-0.resend_info':'1',
                                        'invitations-0.remove':'1'})
        renderer = testing.registerDummyRenderer('templates/manage_members.pt')
        self._callFUT(context, request)
        
        self.assertEqual(0, len(mailer))
        
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

class DummyMembers(testing.DummyModel):
    def __init__(self):
        testing.DummyModel.__init__(self)
        self.__parent__ = karltesting.DummyCommunity()
        self.__name__ = 'members'

# temporary before bfg 0.7.0
class StringTemplateRenderer(testing.DummyTemplateRenderer):
    """
    An instance of this class is returned from
    ``registerDummyRenderer``.  It has a helper function (``assert_``)
    that makes it possible to make an assertion which compares data
    passed to the renderer by the view function against expected
    key/value pairs. 
    """

    def __init__(self, string_response=''):
        testing.DummyTemplateRenderer.__init__(self)
        self.string_response = string_response
        
    def __call__(self, **kw):
        self._received.update(kw)
        return self.string_response

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
