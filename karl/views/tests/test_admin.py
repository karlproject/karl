from __future__ import with_statement

import unittest

from repoze.bfg import testing
from karl import testing as karltesting

from zope.testing.cleanup import cleanUp

class TestAdminView(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def test_it(self):
        from karl.views.admin import admin_view
        site = DummyModel()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
            'templates/admin/admin.pt'
        )
        response = admin_view(site, request)
        self.assertEqual(response.status_int, 200)

class TestDeleteContentView(unittest.TestCase):
    def setUp(self):
        cleanUp()

        from datetime import datetime
        site = DummyModel()
        self.site = site
        profiles = site['profiles'] = DummyModel()

        site['bigendians'] = c = DummyModel()
        c.title = 'Big Endians'
        c.modified = datetime(2009, 12, 23, 12, 31)
        c.creator = 'chucknorris'

        site['littleendians'] = c = DummyModel()
        c.title = 'Little Endians'
        c.modified = datetime(2009, 12, 26, 3, 31)
        c.creator = 'geekbill'

        p = profiles['chucknorris'] = karltesting.DummyProfile()
        p.title = 'Chuck Norris'
        p = profiles['geekbill'] = karltesting.DummyProfile()
        p.title = 'Bill Haverchuck'

        from karl.models.interfaces import ICatalogSearch
        from zope.interface import Interface
        search = DummyCatalogSearch()
        def dummy_search_factory(context):
            return search
        karltesting.registerAdapter(dummy_search_factory, Interface,
                                    ICatalogSearch)
        self.search = search

        from karl.views.admin import delete_content_view
        self.fut = delete_content_view

    def tearDown(self):
        cleanUp()

    def test_render_form(self):
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
            'templates/admin/delete_content.pt'
        )
        self.search.add_result([
            self.site['bigendians'],
            self.site['littleendians'],
        ])

        response = self.fut(self.site, request)
        self.assertEqual(renderer.filtered_content, [])
        c = renderer.communities
        self.assertEqual(len(c), 2)
        self.assertEqual(c[0]['path'], "/bigendians")
        self.assertEqual(c[0]['title'], "Big Endians")
        self.assertEqual(c[1]['path'], "/littleendians")
        self.assertEqual(c[1]['title'], "Little Endians")

    def test_filter_content_no_filter(self):
        renderer = testing.registerDummyRenderer(
            'templates/admin/delete_content.pt'
        )
        self.search.add_result([
            self.site['bigendians'],
            self.site['littleendians'],
        ])
        self.search.add_result([
            self.site['bigendians'],
            self.site['littleendians'],
        ])

        request = testing.DummyRequest(
            params=dict(
                filter_content=1,
            )
        )
        response = self.fut(self.site, request)
        c = renderer.filtered_content
        self.assertEqual(len(c), 0)

    def test_filter_content_by_title(self):
        renderer = testing.registerDummyRenderer(
            'templates/admin/delete_content.pt'
        )
        self.search.add_result([
            self.site['bigendians'],
            self.site['littleendians'],
        ])
        self.search.add_result([
            self.site['bigendians'],
            self.site['littleendians'],
        ])

        request = testing.DummyRequest(
            params=dict(
                filter_content=1,
                title_contains="Little",
            )
        )
        response = self.fut(self.site, request)
        c = renderer.filtered_content
        self.assertEqual(len(c), 1)
        self.assertEqual(c[0]['path'], "/littleendians")
        self.assertEqual(c[0]['url'], "http://example.com/littleendians/")
        self.assertEqual(c[0]['title'], "Little Endians")
        self.assertEqual(c[0]['modified'], "12/26/2009 03:31")
        self.assertEqual(c[0]['creator_name'], "Bill Haverchuck")
        self.assertEqual(c[0]['creator_url'],
                         "http://example.com/profiles/geekbill/")
        self.failUnless(self.site['littleendians'].deactivated)

    def test_filter_content_by_community(self):
        renderer = testing.registerDummyRenderer(
            'templates/admin/delete_content.pt'
        )
        self.search.add_result([
            self.site['bigendians'],
            self.site['littleendians'],
        ])
        self.search.add_result([
            self.site['bigendians'],
            self.site['littleendians'],
        ])

        request = testing.DummyRequest(
            params=dict(
                filter_content=1,
                community='/bigendians',
            )
        )
        response = self.fut(self.site, request)
        self.assertEqual(len(self.search.calls), 2)
        self.assertEqual(self.search.calls[0]['path'], '/bigendians')

    def test_delete_one_item(self):
        from webob.multidict import MultiDict
        request = testing.DummyRequest(
            params=MultiDict([
                ('delete_content', '1'),
                ('selected_content', '/bigendians'),
            ]),
            view_name='delete_content.html',
        )
        self.failUnless('bigendians' in self.site)
        response = self.fut(self.site, request)
        self.assertEqual(
            response.location,
            "http://example.com/delete_content.html"
            "?status_message=Deleted+one+content+item."
        )
        self.failIf('bigendians' in self.site)
        self.failUnless('littleendians' in self.site)

    def test_delete_two_items(self):
        from webob.multidict import MultiDict
        request = testing.DummyRequest(
            params=MultiDict([
                ('delete_content', '1'),
                ('selected_content', '/bigendians'),
                ('selected_content', '/littleendians'),
            ]),
            view_name='delete_content.html',
        )
        self.failUnless('bigendians' in self.site)
        self.failUnless('littleendians' in self.site)
        response = self.fut(self.site, request)
        self.assertEqual(
            response.location,
            "http://example.com/delete_content.html"
            "?status_message=Deleted+2+content+items."
        )
        self.failIf('bigendians' in self.site)
        self.failIf('littleendians' in self.site)

class TestMoveContentView(unittest.TestCase):
    def setUp(self):
        cleanUp()

        from karl.models.interfaces import ICommunity
        from zope.interface import directlyProvides

        from datetime import datetime
        site = DummyModel()
        self.site = site
        profiles = site['profiles'] = DummyModel()

        site['bigendians'] = c = DummyModel()
        directlyProvides(c, ICommunity)
        c.title = 'Big Endians'
        c.modified = datetime(2009, 12, 23, 12, 31)
        c.creator = 'chucknorris'

        blog = c['blog'] = DummyModel()
        entry = blog['entry1'] = DummyModel()
        entry.title = 'Blog Post 1'
        entry.modified = datetime(2009, 12, 23, 12, 31)
        entry.creator = 'chucknorris'

        entry = blog['entry2'] = DummyModel()
        entry.title = 'Blog Post 2'
        entry.modified = datetime(2009, 12, 23, 13, 31)
        entry.creator = 'chucknorris'

        site['littleendians'] = c = DummyModel()
        directlyProvides(c, ICommunity)
        c.title = 'Little Endians'
        c.modified = datetime(2009, 12, 26, 3, 31)
        c.creator = 'geekbill'
        c['blog'] = DummyModel()

        p = profiles['chucknorris'] = karltesting.DummyProfile()
        p.title = 'Chuck Norris'
        p = profiles['geekbill'] = karltesting.DummyProfile()
        p.title = 'Bill Haverchuck'

        from karl.models.interfaces import ICatalogSearch
        from zope.interface import Interface
        search = DummyCatalogSearch()
        def dummy_search_factory(context):
            return search
        karltesting.registerAdapter(dummy_search_factory, Interface,
                                    ICatalogSearch)
        self.search = search

        from karl.views.admin import move_content_view
        self.fut = move_content_view

    def tearDown(self):
        cleanUp()

    def test_render_form(self):
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer(
            'templates/admin/move_content.pt'
        )
        self.search.add_result([
            self.site['bigendians'],
            self.site['littleendians'],
        ])

        response = self.fut(self.site, request)
        self.assertEqual(renderer.filtered_content, [])
        c = renderer.communities
        self.assertEqual(len(c), 2)
        self.assertEqual(c[0]['path'], "/bigendians")
        self.assertEqual(c[0]['title'], "Big Endians")
        self.assertEqual(c[1]['path'], "/littleendians")
        self.assertEqual(c[1]['title'], "Little Endians")

    def test_filter_content_no_filter(self):
        renderer = testing.registerDummyRenderer(
            'templates/admin/move_content.pt'
        )
        self.search.add_result([
            self.site['bigendians'],
            self.site['littleendians'],
        ])
        self.search.add_result([
            self.site['bigendians'],
            self.site['littleendians'],
        ])

        request = testing.DummyRequest(
            params=dict(
                filter_content=1,
            )
        )
        response = self.fut(self.site, request)
        c = renderer.filtered_content
        self.assertEqual(len(c), 0)

    def test_move_one_item(self):
        from webob.multidict import MultiDict
        request = testing.DummyRequest(
            params=MultiDict([
                ('move_content', '1'),
                ('selected_content', '/bigendians/blog/entry1'),
                ('to_community', '/littleendians'),
            ]),
            view_name='move_content.html',
        )
        src_blog = self.site['bigendians']['blog']
        dst_blog = self.site['littleendians']['blog']
        self.failUnless('entry1' in src_blog)
        self.failIf('entry1' in dst_blog)
        response = self.fut(self.site, request)
        self.assertEqual(
            response.location,
            "http://example.com/move_content.html"
            "?status_message=Moved+one+content+item."
        )
        self.failIf('entry1' in src_blog)
        self.failUnless('entry1' in dst_blog)
        self.failUnless('entry2' in src_blog)
        self.failIf('entry2' in dst_blog)

    def test_error_no_to_community(self):
        renderer = testing.registerDummyRenderer(
            'templates/admin/move_content.pt'
        )
        from webob.multidict import MultiDict
        request = testing.DummyRequest(
            params=MultiDict([
                ('move_content', '1'),
                ('selected_content', '/bigendians/blog/entry1'),
            ]),
            view_name='move_content.html',
        )
        response = self.fut(self.site, request)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(renderer.api.error_message,
                         'Please specify destination community.')

    def test_move_two_items(self):
        from webob.multidict import MultiDict
        request = testing.DummyRequest(
            params=MultiDict([
                ('move_content', '1'),
                ('selected_content', '/bigendians/blog/entry1'),
                ('selected_content', '/bigendians/blog/entry2'),
                ('to_community', '/littleendians'),
            ]),
            view_name='move_content.html',
        )
        src_blog = self.site['bigendians']['blog']
        dst_blog = self.site['littleendians']['blog']
        self.failUnless('entry1' in src_blog)
        self.failIf('entry1' in dst_blog)
        self.failUnless('entry2' in src_blog)
        self.failIf('entry2' in dst_blog)
        response = self.fut(self.site, request)
        self.assertEqual(
            response.location,
            "http://example.com/move_content.html"
            "?status_message=Moved+2+content+items."
        )
        self.failIf('entry1' in src_blog)
        self.failUnless('entry1' in dst_blog)
        self.failIf('entry2' in src_blog)
        self.failUnless('entry2' in dst_blog)

    def test_move_bad_destination(self):
        from webob.multidict import MultiDict
        request = testing.DummyRequest(
            params=MultiDict([
                ('move_content', '1'),
                ('selected_content', '/bigendians/blog/entry1'),
                ('to_community', '/littleendians'),
            ]),
            view_name='move_content.html',
        )
        renderer = testing.registerDummyRenderer(
            'templates/admin/move_content.pt'
        )
        del self.site['littleendians']['blog']
        self.fut(self.site, request)
        self.assertEqual(
            renderer.api.error_message,
            'Path does not exist in destination community: /littleendians/blog'
        )

class TestEmailUsersView(unittest.TestCase):
    def setUp(self):
        cleanUp()

        from karl.testing import DummyMailer
        from repoze.sendmail.interfaces import IMailDelivery
        self.mailer = DummyMailer()
        testing.registerUtility(self.mailer, IMailDelivery)

        site = self.site = testing.DummyModel()
        profiles = site['profiles'] = testing.DummyModel()
        users = site.users = karltesting.DummyUsers()
        fred = profiles['fred'] = testing.DummyModel(
            title='Fred Flintstone', email='fred@example.com'
        )
        barney = profiles['barney'] = testing.DummyModel(
            title='Barney Rubble', email='barney@example.com'
        )
        users._by_id = users._by_login = {
            'fred': {
                'groups': ['group.KarlStaff'],
            },
            'barney': {
                'groups': ['group.KarlAdmin'],
            }
        }

        from repoze.bfg.interfaces import ISettings
        testing.registerUtility(karltesting.DummySettings(), ISettings)

        from karl.models.interfaces import ICatalogSearch
        from zope.interface import Interface
        search = DummyCatalogSearch()
        def dummy_search_factory(context):
            return search
        karltesting.registerAdapter(dummy_search_factory, Interface,
                                    ICatalogSearch)
        search.add_result([fred, barney])

    def tearDown(self):
        cleanUp()

    def _make_one(self, context, request):
        from karl.views.admin import EmailUsersView
        return EmailUsersView(context, request)

    def test_render_form(self):
        request = testing.DummyRequest()
        testing.registerDummySecurityPolicy('barney')
        view = self._make_one(self.site, request)
        renderer = testing.registerDummyRenderer(
            'templates/admin/email_users.pt'
        )
        response = view()
        self.assertEqual(response.status_int, 200)
        self.assertEqual(renderer.to_groups, view.to_groups)
        self.assertEqual(renderer.from_emails, [
            ('self', 'Barney Rubble <barney@example.com>'),
            ('admin', 'karl3test Administrator <admin@example.com>'),
        ])

    def test_email_everyone(self):
        from webob.multidict import MultiDict
        request = testing.DummyRequest(params=MultiDict({
            'from_email': 'self',
            'to_group': '',
            'subject': 'Exciting news!',
            'text': 'Foo walked into a bar...',
            'send_email': '1',
        }))
        testing.registerDummySecurityPolicy('barney')
        view = self._make_one(self.site, request)
        response = view()
        self.assertEqual(response.location,
                         'http://example.com/admin.html'
                         '?status_message=Sent+message+to+2+users.')
        self.assertEqual(len(self.mailer), 2)
        self.assertEqual(self.mailer[0].mfrom, 'barney@example.com')

        from email.parser import Parser
        msg = Parser().parsestr(self.mailer[0].msg)
        self.assertEqual(msg['Subject'], 'Exciting news!')
        body = msg.get_payload(decode=True)
        self.failUnless('Foo walked into a bar' in body, body)

    def test_email_staff(self):
        from webob.multidict import MultiDict
        request = testing.DummyRequest(params=MultiDict({
            'from_email': 'admin',
            'to_group': 'group.KarlStaff',
            'subject': 'Exciting news!',
            'text': 'Foo walked into a bar...',
            'send_email': '1',
        }))
        testing.registerDummySecurityPolicy('barney')
        view = self._make_one(self.site, request)
        response = view()
        self.assertEqual(response.location,
                         'http://example.com/admin.html'
                         '?status_message=Sent+message+to+1+users.')
        self.assertEqual(len(self.mailer), 1)
        self.assertEqual(self.mailer[0].mfrom, 'admin@example.com')

        from email.parser import Parser
        msg = Parser().parsestr(self.mailer[0].msg)
        self.assertEqual(msg['Subject'], 'Exciting news!')
        self.assertEqual(msg['From'],
                         'karl3test Administrator <admin@example.com>')
        self.assertEqual(msg['To'], 'Fred Flintstone <fred@example.com>')
        body = msg.get_payload(decode=True)
        self.failUnless('Foo walked into a bar' in body, body)

class TestSyslogView(unittest.TestCase):
    def setUp(self):
        cleanUp()

        import os
        import sys
        here = os.path.abspath(os.path.dirname(sys.modules[__name__].__file__))
        from repoze.bfg.interfaces import ISettings
        self.settings = settings = karltesting.DummySettings(
            syslog_view=os.path.join(here, 'test.log'),
            syslog_view_instances=['org1', 'org2'],
        )
        testing.registerUtility(settings, ISettings)

        from karl.views.admin import syslog_view
        self.fut = syslog_view

    def tearDown(self):
        cleanUp()

    def test_no_filter(self):
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer('templates/admin/syslog.pt')
        response = self.fut(None, request)
        self.assertEqual(len(renderer.entries), 4)
        self.assertEqual(renderer.instance, '_any')
        self.failUnless(renderer.entries[0].startswith('Dec 26 11:15:23'))

    def test_filter_any(self):
        request = testing.DummyRequest(params={
            'instance': '_any',
        })
        renderer = testing.registerDummyRenderer('templates/admin/syslog.pt')
        response = self.fut(None, request)
        self.assertEqual(len(renderer.entries), 4)
        self.assertEqual(renderer.instances, ['org1', 'org2'])
        self.assertEqual(renderer.instance, '_any')
        self.failUnless(renderer.entries[0].startswith('Dec 26 11:15:23'))

    def test_filter_org1(self):
        request = testing.DummyRequest(params={
            'instance': 'org1',
        })
        renderer = testing.registerDummyRenderer('templates/admin/syslog.pt')
        response = self.fut(None, request)
        self.assertEqual(len(renderer.entries), 2)
        self.assertEqual(renderer.instances, ['org1', 'org2'])
        self.assertEqual(renderer.instance, 'org1')
        self.failUnless(renderer.entries[0].startswith('Dec 26 11:14:23'))

    def test_single_digit_day_with_leading_space(self):
        self.settings['syslog_view_instances'] = ['org1', 'org2', 'org3']
        request = testing.DummyRequest(params={
            'instance': 'org3',
        })
        renderer = testing.registerDummyRenderer('templates/admin/syslog.pt')
        response = self.fut(None, request)
        self.assertEqual(len(renderer.entries), 1)
        self.assertEqual(renderer.instances, ['org1', 'org2', 'org3'])
        self.assertEqual(renderer.instance, 'org3')
        self.failUnless(renderer.entries[0].startswith('Feb  2 11:15:23'))

class TestLogsView(unittest.TestCase):
    def setUp(self):
        cleanUp()

        import os
        import sys
        here = os.path.abspath(os.path.dirname(sys.modules[__name__].__file__))
        from repoze.bfg.interfaces import ISettings

        self.logs = [os.path.join(here, 'test.log'),
                     os.path.join(here, 'test_admin.py')]
        settings = karltesting.DummySettings(
            logs_view=self.logs
        )
        testing.registerUtility(settings, ISettings)

        from karl.views.admin import logs_view
        self.fut = logs_view

    def tearDown(self):
        cleanUp()

    def test_no_log(self):
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer('templates/admin/log.pt')
        response = self.fut(None, request)
        self.assertEqual(len(renderer.logs), 2)
        self.assertEqual(renderer.log, None)
        self.assertEqual(len(renderer.lines), 0)

    def test_view_log(self):
        request = testing.DummyRequest(params={
            'log': self.logs[0]
        })
        renderer = testing.registerDummyRenderer('templates/admin/log.pt')
        response = self.fut(None, request)
        self.assertEqual(renderer.logs, self.logs)
        self.assertEqual(renderer.log, self.logs[0])
        self.assertEqual(len(renderer.lines), 6)

    def test_one_log(self):
        del self.logs[1]
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer('templates/admin/log.pt')
        response = self.fut(None, request)
        self.assertEqual(len(renderer.logs), 1)
        self.assertEqual(renderer.log, self.logs[0])
        self.assertEqual(len(renderer.lines), 6)

    def test_protect_arbitrary_files(self):
        request = testing.DummyRequest(params={
            'log': self.logs[0]
        })
        self.logs[0] = 'foo'
        renderer = testing.registerDummyRenderer('templates/admin/log.pt')
        response = self.fut(None, request)
        self.assertEqual(renderer.log, None)
        self.assertEqual(len(renderer.lines), 0)

class TestUploadUsersView(unittest.TestCase):
    def setUp(self):
        cleanUp()

        site = testing.DummyModel()
        profiles = site['profiles'] = testing.DummyModel()
        encrypt = lambda x: 'sha:' + x
        users = site.users = karltesting.DummyUsers(encrypt=encrypt)
        self.site = site

        self.renderer = testing.registerDummyRenderer(
            'templates/admin/upload_users_csv.pt'
        )

        from repoze.lemonade.testing import registerContentFactory
        from karl.models.interfaces import IProfile
        registerContentFactory(testing.DummyModel, IProfile)

        from repoze.workflow.testing import registerDummyWorkflow
        registerDummyWorkflow('security')

    def tearDown(self):
        cleanUp()

    def _call_fut(self, context, request):
        from karl.views.admin import UploadUsersView
        return UploadUsersView(context, request)()

    def _file_upload(self, fname):
        import os, sys
        here = os.path.dirname(sys.modules[__name__].__file__)
        return DummyUpload(None, path=os.path.join(here, fname))

    def test_render_form(self):
        request = testing.DummyRequest()
        response = self._call_fut(self.site, request)
        self.assertEqual(response.status_int, 200)
        self.failUnless(hasattr(self.renderer, 'menu'))
        self.failUnless(hasattr(self.renderer, 'required_fields'))
        self.failUnless(hasattr(self.renderer, 'allowed_fields'))

    def test_submit_ok(self):
        request = testing.DummyRequest({
            'csv': self._file_upload('test_users1.csv'),
        })
        response = self._call_fut(self.site, request)
        self.assertEqual(response.status_int, 200)

        api = self.renderer.api
        self.assertEqual(api.error_message, None)
        self.assertEqual(api.status_message, "Created 2 users.")

        users = self.site.users
        self.assertEqual(users.get_by_id('user1'), {
            'id': 'user1',
            'login': 'hello sir',
            'password': 'sha:pass1234',
            'groups': set(['group.KarlAdmin', 'group.community.moderator']),
        })

        self.assertEqual(users.get_by_id('user2'), {
            'id': 'user2',
            'login': 'user2',
            'password': 'sha:pass1234',
            'groups': set(),
        })

        profile = self.site['profiles']['user1']
        self.assertEqual(profile.email, 'user1@example.com')
        self.assertEqual(profile.firstname, 'User')
        self.assertEqual(profile.lastname, 'One')
        self.assertEqual(profile.phone, '(212) 555-1212')
        self.assertEqual(profile.extension, 'x33')
        self.assertEqual(profile.department, 'Homeland Ambiguity')
        self.assertEqual(profile.position, 'High Sheriff')
        self.assertEqual(profile.organization, 'Not much')
        self.assertEqual(profile.location, 'Down yonder')
        self.assertEqual(profile.country, 'US and A')
        self.assertEqual(profile.website, 'http://example.com')
        self.assertEqual(profile.languages, 'Turkish, Ebonics')
        self.assertEqual(profile.office, '1234')
        self.assertEqual(profile.room_no, '12')
        self.assertEqual(profile.biography, 'Born.  Not dead yet.')
        self.assertEqual(profile.home_path, '/offices/ha')

        profile = self.site['profiles']['user2']
        self.assertEqual(profile.email, 'user2@example.com')
        self.assertEqual(profile.firstname, 'User')
        self.assertEqual(profile.lastname, 'Two')
        self.assertEqual(profile.phone, '(212) 555-1212')
        self.assertEqual(profile.extension, 'x34')
        self.assertEqual(profile.department, 'Homeland Ambiguity')
        self.assertEqual(profile.position, 'High Sheriff')
        self.assertEqual(profile.organization, 'A little')
        self.assertEqual(profile.location, 'Over there')
        self.assertEqual(profile.country, 'US and A')
        self.assertEqual(profile.website, 'http://example.com')
        self.assertEqual(profile.languages, 'Magyar, Klingon')
        self.assertEqual(profile.office, '4321')
        self.assertEqual(profile.room_no, '21')
        self.assertEqual(profile.biography, '')
        self.assertEqual(profile.home_path, '')

    def test_password_encrypted(self):
        request = testing.DummyRequest({
            'csv': DummyUpload(
                '"username","firstname","lastname","email","sha_password"\n'
                '"user1","User","One","test@example.com","pass1234"\n'
                ),
        })
        response = self._call_fut(self.site, request)

        api = self.renderer.api
        self.assertEqual(api.error_message, None)
        self.assertEqual(api.status_message, "Created 1 users.")

        users = self.site.users
        self.assertEqual(users.get_by_id('user1')['password'], 'pass1234')

    def test_row_too_long(self):
        request = testing.DummyRequest({
            'csv': DummyUpload(
                '"username","firstname","lastname","email","sha_password"\n'
                '"user1","User","One","test@example.com","pass1234","foo"\n'
                ),
        })
        response = self._call_fut(self.site, request)

        api = self.renderer.api
        self.assertEqual(api.error_message,
                         'Malformed CSV: line 2 does not match header.')
        self.assertEqual(api.status_message, None)

    def test_row_too_short(self):
        request = testing.DummyRequest({
            'csv': DummyUpload(
                '"username","firstname","lastname","email","sha_password"\n'
                '"user1","User","One","test@example.com"\n'
                ),
        })
        response = self._call_fut(self.site, request)

        api = self.renderer.api
        self.assertEqual(api.error_message,
                         'Malformed CSV: line 2 does not match header.')
        self.assertEqual(api.status_message, None)

    def test_test_unknown_field(self):
        request = testing.DummyRequest({
            'csv': DummyUpload(
            '"username","firstname","lastname","email","sha_password","wut"\n'
            '"user1","User","One","test@example.com","pass1234","wut"\n'
            ),
        })
        response = self._call_fut(self.site, request)

        api = self.renderer.api
        self.assertEqual(api.error_message,
                         'Unrecognized field: wut')
        self.assertEqual(api.status_message, None)

    def test_missing_required_field(self):
        request = testing.DummyRequest({
            'csv': DummyUpload(
                '"username","lastname","email","sha_password"\n'
                '"user1","One","test@example.com","pass1234"\n'
                ),
        })
        response = self._call_fut(self.site, request)

        api = self.renderer.api
        self.assertEqual(api.error_message,
                         'Missing required field: firstname')
        self.assertEqual(api.status_message, None)

    def test_missing_password_field(self):
        request = testing.DummyRequest({
            'csv': DummyUpload(
                '"username","firstname","lastname","email"\n'
                '"user1","User","One","test@example.com"\n'
                ),
        })
        response = self._call_fut(self.site, request)

        api = self.renderer.api
        self.assertEqual(api.error_message,
                         'Must supply either password or sha_password field.')
        self.assertEqual(api.status_message, None)

    def test_skip_existing_user_in_users(self):
        self.site.users.add('user1', 'user1', 'password', set())
        request = testing.DummyRequest({
            'csv': DummyUpload(
                '"username","firstname","lastname","email","password"\n'
                '"user1","User","One","test@example.com","pass1234"\n'
                '"user2","User","Two","test@example.com","pass1234"\n'
                ),
        })
        response = self._call_fut(self.site, request)

        api = self.renderer.api
        self.assertEqual(api.error_message, None)
        self.assertEqual(api.status_message,
                          'Skipping user: user1: User already exists.\n'
                          'Created 1 users.')

    def test_skip_existing_user_in_profiles(self):
        self.site['profiles']['user1'] = testing.DummyModel()
        request = testing.DummyRequest({
            'csv': DummyUpload(
                '"username","firstname","lastname","email","password"\n'
                '"user1","User","One","test@example.com","pass1234"\n'
                '"user2","User","Two","test@example.com","pass1234"\n'
                ),
        })
        response = self._call_fut(self.site, request)

        api = self.renderer.api
        self.assertEqual(api.error_message, None)
        self.assertEqual(api.status_message,
                          'Skipping user: user1: User already exists.\n'
                          'Created 1 users.')


    def test_skip_existing_user_by_login(self):
        self.site.users.add('foo', 'user1', 'password', set())
        request = testing.DummyRequest({
            'csv': DummyUpload(
                '"username","firstname","lastname","email","password"\n'
                '"user1","User","One","test@example.com","pass1234"\n'
                '"user2","User","Two","test@example.com","pass1234"\n'
                ),
        })
        response = self._call_fut(self.site, request)

        api = self.renderer.api
        self.assertEqual(api.error_message, None)
        self.assertEqual(api.status_message,
                'Skipping user: user1: User already exists with login: user1\n'
                'Created 1 users.')

class TestErrorMonitorView(unittest.TestCase):
    def setUp(self):
        cleanUp()

        import tempfile
        self.tmpdir = tmpdir = tempfile.mkdtemp('karl_test')

        self.site = testing.DummyModel()

        from repoze.bfg.interfaces import ISettings
        settings = karltesting.DummySettings(
            error_monitor_dir=tmpdir,
            error_monitor_subsystems=["blonde", "red", "head"],
        )
        testing.registerUtility(settings, ISettings)

    def log_error(self, subsystem, message):
        import os
        with open(os.path.join(self.tmpdir, subsystem), 'ab') as f:
            print >>f, 'ENTRY'
            print >>f, message

    def tearDown(self):
        cleanUp()

        import shutil
        shutil.rmtree(self.tmpdir)

    def call_fut(self):
        from karl.views.admin import error_monitor_view
        request = testing.DummyRequest()
        return error_monitor_view(self.site, request)

    def test_all_ok(self):
        renderer = testing.registerDummyRenderer(
            'templates/admin/error_monitor.pt'
        )
        self.call_fut()
        self.assertEqual(renderer.subsystems, ["blonde", "red", "head"])
        self.assertEqual(renderer.states,
                         {"blonde": [], "red": [], "head": []})
        self.assertEqual(renderer.urls['blonde'],
            "http://example.com/error_monitor_subsystem.html?subsystem=blonde")

    def test_bad_head(self):
        renderer = testing.registerDummyRenderer(
            'templates/admin/error_monitor.pt'
        )
        self.log_error('head', 'Testing...')
        self.call_fut()
        self.assertEqual(renderer.states,
                         {"blonde": [], "red": [], "head": ['Testing...']})

class TestErrorMonitorSubsystemView(unittest.TestCase):
    def setUp(self):
        cleanUp()

        import tempfile
        self.tmpdir = tmpdir = tempfile.mkdtemp('karl_test')

        self.site = testing.DummyModel()

        from repoze.bfg.interfaces import ISettings
        settings = karltesting.DummySettings(
            error_monitor_dir=tmpdir,
            error_monitor_subsystems=["blonde", "red", "head"],
        )
        testing.registerUtility(settings, ISettings)

    def log_error(self, subsystem, message):
        import os
        with open(os.path.join(self.tmpdir, subsystem), 'ab') as f:
            print >>f, 'ENTRY'
            print >>f, message

    def tearDown(self):
        cleanUp()

        import shutil
        shutil.rmtree(self.tmpdir)

    def call_fut(self, subsystem=None):
        from karl.views.admin import error_monitor_subsystem_view
        request = testing.DummyRequest(params={})
        if subsystem is not None:
            request.params['subsystem'] = subsystem
        return error_monitor_subsystem_view(self.site, request)

    def test_no_subsystem(self):
        renderer = testing.registerDummyRenderer(
            'templates/admin/error_monitor_subsystem.pt'
        )
        from repoze.bfg.exceptions import NotFound
        self.assertRaises(NotFound, self.call_fut)

    def test_no_errors(self):
        renderer = testing.registerDummyRenderer(
            'templates/admin/error_monitor_subsystem.pt'
        )
        self.call_fut('red')
        self.assertEqual(renderer.entries, [])

    def test_bad_head(self):
        renderer = testing.registerDummyRenderer(
            'templates/admin/error_monitor_subsystem.pt'
        )
        self.log_error('head', 'foo')
        self.log_error('head', 'bar')
        self.call_fut('head')
        self.assertEqual(renderer.entries, ['foo', 'bar'])

class TestErrorMonitorStatusView(unittest.TestCase):
    def setUp(self):
        cleanUp()

        import tempfile
        self.tmpdir = tmpdir = tempfile.mkdtemp('karl_test')

        self.site = testing.DummyModel()

        from repoze.bfg.interfaces import ISettings
        settings = karltesting.DummySettings(
            error_monitor_dir=tmpdir,
            error_monitor_subsystems=["blonde", "red", "head"],
        )
        testing.registerUtility(settings, ISettings)

    def log_error(self, subsystem, message):
        import os
        with open(os.path.join(self.tmpdir, subsystem), 'ab') as f:
            print >>f, 'ENTRY'
            print >>f, message

    def tearDown(self):
        cleanUp()

        import shutil
        shutil.rmtree(self.tmpdir)

    def call_fut(self):
        from karl.views.admin import error_monitor_status_view
        request = testing.DummyRequest()
        return error_monitor_status_view(self.site, request)

    def test_all_ok(self):
        body = self.call_fut().body
        self.assertEqual(body, "blonde: OK\n"
                               "red: OK\n"
                               "head: OK\n")

    def test_bad_head(self):
        self.log_error('head', 'foo')
        body = self.call_fut().body
        self.assertEqual(body, "blonde: OK\n"
                               "red: OK\n"
                               "head: ERROR\n")

class DummyCatalogSearch(object):
    def __init__(self):
        self._results = []
        self.calls = []

    def add_result(self, result):
        self._results.append(result)

    def __call__(self, **kw):
        self.calls.append(kw)
        if self._results:
            result = self._results.pop(0)
            count = len(result)
            def resolver(i):
                return result[i]
            return count, xrange(count), resolver
        return 0, (), None

class DummyModel(testing.DummyModel):
    deactivated = False

    def _p_deactivate(self):
        self.deactivated = True

class DummyUpload(object):
    type = 'text/plain'
    filename = 'users.csv'

    def __init__(self, data, path=None):
        if path is not None:
            self.file = open(path, "rb")
        else:
            from cStringIO import StringIO
            self.file = StringIO(data)
