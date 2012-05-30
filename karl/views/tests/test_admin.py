from __future__ import with_statement

import mock
import unittest

from pyramid import testing
from karl import testing as karltesting

class TestAdminView(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def test_it(self):
        karltesting.registerDummyRenderer('karl.views:templates/admin/menu.pt')
        from karl.views.admin import admin_view
        site = DummyModel()
        request = testing.DummyRequest()
        result = admin_view(site, request)
        self.failUnless('api' in result)

class TestDeleteContentView(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

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
        karltesting.registerDummyRenderer('karl.views:templates/admin/menu.pt')
        karltesting.registerDummyRenderer(
            'karl.views:templates/admin/content_select.pt')

    def tearDown(self):
        testing.cleanUp()

    def test_render_form(self):
        request = testing.DummyRequest()
        self.search.add_result([
            self.site['bigendians'],
            self.site['littleendians'],
        ])

        result = self.fut(self.site, request)
        self.assertEqual(result['filtered_content'], [])
        c = result['communities']
        self.assertEqual(len(c), 2)
        self.assertEqual(c[0]['path'], "/bigendians")
        self.assertEqual(c[0]['title'], "Big Endians")
        self.assertEqual(c[1]['path'], "/littleendians")
        self.assertEqual(c[1]['title'], "Little Endians")

    def test_filter_content_no_filter(self):
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
        result = self.fut(self.site, request)
        c = result['filtered_content']
        self.assertEqual(len(c), 0)

    def test_filter_content_by_title(self):
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
        result = self.fut(self.site, request)
        c = result['filtered_content']
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
        self.fut(self.site, request)
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

    def test_delete_nested_items(self):
        parent = self.site['bigendians']
        parent['macrobots'] = DummyModel()

        from webob.multidict import MultiDict
        request = testing.DummyRequest(
            params=MultiDict([
                ('delete_content', '1'),
                ('selected_content', '/bigendians'),
                ('selected_content', '/bigendians/macrobots'),
            ]),
            view_name='delete_content.html',
        )
        self.failUnless('bigendians' in self.site)
        response = self.fut(self.site, request)
        self.assertEqual(
            response.location,
            "http://example.com/delete_content.html"
            "?status_message=Deleted+2+content+items."
        )
        self.failIf('bigendians' in self.site)

class TestMoveContentView(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

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
        karltesting.registerDummyRenderer('karl.views:templates/admin/menu.pt')
        karltesting.registerDummyRenderer(
            'karl.views:templates/admin/content_select.pt')
    def tearDown(self):
        testing.cleanUp()

    def test_render_form(self):
        request = testing.DummyRequest()
        self.search.add_result([
            self.site['bigendians'],
            self.site['littleendians'],
        ])

        result = self.fut(self.site, request)
        self.assertEqual(result['filtered_content'], [])
        c = result['communities']
        self.assertEqual(len(c), 2)
        self.assertEqual(c[0]['path'], "/bigendians")
        self.assertEqual(c[0]['title'], "Big Endians")
        self.assertEqual(c[1]['path'], "/littleendians")
        self.assertEqual(c[1]['title'], "Little Endians")

    def test_filter_content_no_filter(self):
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
        result = self.fut(self.site, request)
        c = result['filtered_content']
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
        from webob.multidict import MultiDict
        request = testing.DummyRequest(
            params=MultiDict([
                ('move_content', '1'),
                ('selected_content', '/bigendians/blog/entry1'),
            ]),
            view_name='move_content.html',
        )
        result = self.fut(self.site, request)
        self.assertEqual(result['api'].error_message,
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
        del self.site['littleendians']['blog']
        result = self.fut(self.site, request)
        self.assertEqual(
            result['api'].error_message,
            'Path does not exist in destination community: /littleendians/blog'
        )

class TestSiteAnnouncementView(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()
        self.site = DummyModel()
        karltesting.registerDummyRenderer('karl.views:templates/admin/menu.pt')

    def tearDown(self):
        testing.cleanUp()

    def call_fut(self, *arg, **kw):
        from karl.views.admin import site_announcement_view
        return site_announcement_view(*arg, **kw)

    def test_render(self):
        request = testing.DummyRequest()
        result = self.call_fut(self.site, request)
        self.failUnless('api' in result)

    def test_set_announcement(self):
        request = testing.DummyRequest()
        request.params['submit-site-announcement'] = None
        annc = '<p>This is the <i>announcement</i>.</p>'
        request.params['site-announcement-input'] = annc
        self.call_fut(self.site, request)
        self.assertEqual(self.site.site_announcement, annc[3:-4])

    def test_set_announcement_drop_extra(self):
        request = testing.DummyRequest()
        request.params['submit-site-announcement'] = None
        annc = '<p>This is the <i>announcement</i>.</p><p>This is dropped.</p>'
        request.params['site-announcement-input'] = annc
        self.call_fut(self.site, request)
        self.assertEqual(self.site.site_announcement, annc[3:35])

    def test_remove_announcement(self):
        self.site.site_announcement = 'Foo.'
        request = testing.DummyRequest()
        request.params['remove-site-announcement'] = None
        self.call_fut(self.site, request)
        self.failIf(self.site.site_announcement)


class TestEmailUsersView(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

        from repoze.sendmail.interfaces import IMailDelivery
        self.mailer = karltesting.DummyMailer()
        karltesting.registerUtility(self.mailer, IMailDelivery)

        site = self.site = testing.DummyModel()
        profiles = site['profiles'] = testing.DummyModel()
        users = site.users = karltesting.DummyUsers()
        fred = profiles['fred'] = testing.DummyModel(
            title='Fred Flintstone', email='fred@example.com'
        )
        barney = profiles['barney'] = testing.DummyModel(
            title='Barney Rubble', email='barney@example.com'
        )
        wilma = profiles['wilma'] = testing.DummyModel(
            title='Wilma', email='wilma@example.com',
            security_state='inactive'
        )
        users._by_id = users._by_login = {
            'fred': {
                'groups': ['group.KarlStaff'],
            },
            'barney': {
                'groups': ['group.KarlAdmin'],
            },
            'wilma': {
                'groups': []
            }
        }

        from pyramid.interfaces import ISettings
        karltesting.registerUtility(karltesting.DummySettings(), ISettings)

        from karl.models.interfaces import ICatalogSearch
        from zope.interface import Interface
        search = DummyCatalogSearch()
        def dummy_search_factory(context):
            return search
        karltesting.registerAdapter(dummy_search_factory, Interface,
                                    ICatalogSearch)
        search.add_result([fred, barney, wilma])
        karltesting.registerDummyRenderer('karl.views:templates/admin/menu.pt')

    def tearDown(self):
        testing.cleanUp()

    def _make_one(self, context, request):
        from karl.views.admin import EmailUsersView
        return EmailUsersView(context, request)

    def test_render_form(self):
        request = testing.DummyRequest()
        karltesting.registerDummySecurityPolicy('barney')
        view = self._make_one(self.site, request)
        result = view()
        self.assertEqual(result['to_groups'], view.to_groups)
        self.assertEqual(result['from_emails'], [
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
        karltesting.registerDummySecurityPolicy('barney')
        view = self._make_one(self.site, request)
        response = view()
        self.assertEqual(response.location,
                         'http://example.com/admin.html'
                         '?status_message=Sent+message+to+2+users.')
        self.assertEqual(len(self.mailer), 2)

        msg = self.mailer[0].msg
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
        karltesting.registerDummySecurityPolicy('barney')
        view = self._make_one(self.site, request)
        response = view()
        self.assertEqual(response.location,
                         'http://example.com/admin.html'
                         '?status_message=Sent+message+to+1+users.')
        self.assertEqual(len(self.mailer), 1)

        msg = self.mailer[0].msg
        self.assertEqual(msg['Subject'], 'Exciting news!')
        self.assertEqual(msg['From'],
                         'karl3test Administrator <admin@example.com>')
        self.assertEqual(msg['To'], 'Fred Flintstone <fred@example.com>')
        body = msg.get_payload(decode=True)
        self.failUnless('Foo walked into a bar' in body, body)

class TestSyslogView(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

        import os
        import sys
        here = os.path.abspath(os.path.dirname(sys.modules[__name__].__file__))
        from pyramid.interfaces import ISettings
        self.settings = settings = karltesting.DummySettings(
            syslog_view=os.path.join(here, 'test.log'),
            syslog_view_instances=['org1', 'org2'],
        )
        karltesting.registerUtility(settings, ISettings)

        from karl.views.admin import syslog_view
        self.fut = syslog_view
        karltesting.registerDummyRenderer('karl.views:templates/admin/menu.pt')

    def tearDown(self):
        testing.cleanUp()

    def test_no_syslog_path(self):
        from pyramid.interfaces import ISettings
        self.settings = settings = karltesting.DummySettings()
        karltesting.registerUtility(settings, ISettings)
        request = testing.DummyRequest()
        result = self.fut(testing.DummyModel(), request)
        batch_info = result['batch_info']
        entries = batch_info['entries']
        self.assertEqual(len(entries), 0)
        self.assertEqual(result['instance'], '_any')


    def test_no_filter(self):
        request = testing.DummyRequest()
        result = self.fut(testing.DummyModel(), request)
        batch_info = result['batch_info']
        entries = batch_info['entries']
        self.assertEqual(len(entries), 4)
        self.assertEqual(result['instance'], '_any')
        self.failUnless(entries[0].startswith('Dec 26 11:15:23'))

    def test_filter_any(self):
        request = testing.DummyRequest(params={
            'instance': '_any',
        })
        result = self.fut(testing.DummyModel(), request)
        self.assertEqual(len(result['batch_info']['entries']), 4)
        self.assertEqual(result['instances'], ['org1', 'org2'])
        self.assertEqual(result['instance'], '_any')
        self.failUnless(
            result['batch_info']['entries'][0].startswith('Dec 26 11:15:23'))

    def test_filter_org1(self):
        request = testing.DummyRequest(params={
            'instance': 'org1',
        })
        result = self.fut(testing.DummyModel(), request)
        self.assertEqual(len(result['batch_info']['entries']), 2)
        self.assertEqual(result['instances'], ['org1', 'org2'])
        self.assertEqual(result['instance'], 'org1')
        self.failUnless(
            result['batch_info']['entries'][0].startswith('Dec 26 11:14:23'))

    def test_single_digit_day_with_leading_space(self):
        self.settings['syslog_view_instances'] = ['org1', 'org2', 'org3']
        request = testing.DummyRequest(params={
            'instance': 'org3',
        })
        result = self.fut(testing.DummyModel(), request)
        self.assertEqual(len(result['batch_info']['entries']), 1)
        self.assertEqual(result['instances'], ['org1', 'org2', 'org3'])
        self.assertEqual(result['instance'], 'org3')
        self.failUnless(
            result['batch_info']['entries'][0].startswith('Feb  2 11:15:23'))

class TestLogsView(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

        import os
        import sys
        here = os.path.abspath(os.path.dirname(sys.modules[__name__].__file__))
        from pyramid.interfaces import ISettings

        self.logs = [os.path.join(here, 'test.log'),
                     os.path.join(here, 'test_admin.py')]
        settings = karltesting.DummySettings(
            logs_view=self.logs
        )
        karltesting.registerUtility(settings, ISettings)

        from karl.views.admin import logs_view
        self.fut = logs_view
        karltesting.registerDummyRenderer('karl.views:templates/admin/menu.pt')

    def tearDown(self):
        testing.cleanUp()

    def test_no_log(self):
        request = testing.DummyRequest()
        result = self.fut(testing.DummyModel(), request)
        self.assertEqual(len(result['logs']), 2)
        self.assertEqual(result['log'], None)
        self.assertEqual(len(result['lines']), 0)

    def test_view_log(self):
        request = testing.DummyRequest(params={
            'log': self.logs[0]
        })
        result = self.fut(testing.DummyModel(), request)
        self.assertEqual(result['logs'], self.logs)
        self.assertEqual(result['log'], self.logs[0])
        self.assertEqual(len(result['lines']), 6)

    def test_one_log(self):
        del self.logs[1]
        request = testing.DummyRequest()
        result = self.fut(testing.DummyModel(), request)
        self.assertEqual(len(result['logs']), 1)
        self.assertEqual(result['log'], self.logs[0])
        self.assertEqual(len(result['lines']), 6)

    def test_protect_arbitrary_files(self):
        request = testing.DummyRequest(params={
            'log': self.logs[0]
        })
        self.logs[0] = 'foo'
        result = self.fut(testing.DummyModel(), request)
        self.assertEqual(result['log'], None)
        self.assertEqual(len(result['lines']), 0)

class TestStatisticsView(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

        import os
        import sys
        here = os.path.abspath(os.path.dirname(sys.modules[__name__].__file__))

        from pyramid.interfaces import ISettings
        self.stats_folder = here

        settings = karltesting.DummySettings(
            statistics_folder=here
        )
        karltesting.registerUtility(settings, ISettings)

        from karl.views.admin import statistics_view
        self.fut = statistics_view
        karltesting.registerDummyRenderer('karl.views:templates/admin/menu.pt')

    def tearDown(self):
        testing.cleanUp()

    def test_it(self):
        request = testing.DummyRequest()
        self.assertEqual(self.fut(testing.DummyModel(), request)['csv_files'],
                         ['test_users1.csv'])

class TestStatisticsCSVView(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

        import os
        import sys
        here = os.path.abspath(os.path.dirname(sys.modules[__name__].__file__))

        from pyramid.interfaces import ISettings
        self.stats_folder = here

        settings = karltesting.DummySettings(
            statistics_folder=here
        )
        karltesting.registerUtility(settings, ISettings)

        from karl.views.admin import statistics_csv_view
        self.fut = statistics_csv_view

    def tearDown(self):
        testing.cleanUp()

    def test_download_csv(self):
        import os
        from pyramid.request import Request
        expected = open(os.path.join(self.stats_folder,
                                     'test_users1.csv')).read()
        request = Request.blank('/')
        request.context = None
        request.matchdict = {'csv_file': 'test_users1.csv'}
        self.assertEqual(self.fut(request).body, expected)

    def test_not_csv(self):
        from pyramid.exceptions import NotFound
        from pyramid.request import Request
        request = Request.blank('/')
        request.context = None
        request.matchdict = {'csv_file': 'test_admin.py'}
        self.assertRaises(NotFound, self.fut, request)

    def test_file_not_found(self):
        from pyramid.exceptions import NotFound
        from pyramid.request import Request
        request = Request.blank('/')
        request.context = None
        request.matchdict = {'csv_file': 'foo.csv'}
        self.assertRaises(NotFound, self.fut, request)

class TestUploadUsersView(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

        site = testing.DummyModel()
        site['profiles'] = DummyProfiles()
        encrypt = lambda x: 'sha:' + x
        site.users = karltesting.DummyUsers(encrypt=encrypt)
        self.site = site

        from repoze.lemonade.testing import registerContentFactory
        from karl.models.interfaces import IProfile
        registerContentFactory(testing.DummyModel, IProfile)

        from repoze.workflow.testing import registerDummyWorkflow
        self.workflow = registerDummyWorkflow('security')
        karltesting.registerDummyRenderer('karl.views:templates/admin/menu.pt')

        self.search_results = {}
        class DummySearch(object):
            def __init__(self, context):
                pass

            def __call__(myself, **kw):
                key = tuple(sorted(kw.items()))
                if key in self.search_results:
                    return self.search_results[key]
                return 0, [], None

        from zope.interface import Interface
        from karl.models.interfaces import ICatalogSearch
        karltesting.registerAdapter(DummySearch, (Interface,), ICatalogSearch)

    def tearDown(self):
        testing.cleanUp()

    def _call_fut(self, context, request, rename_user=None):
        from karl.views.admin import UploadUsersView as cls
        fut = cls(context, request)
        fut.rename_user = rename_user
        return fut()

    def _file_upload(self, fname):
        import os, sys
        here = os.path.dirname(sys.modules[__name__].__file__)
        return DummyUpload(None, path=os.path.join(here, fname))

    def test_render_form(self):
        request = testing.DummyRequest()
        result = self._call_fut(self.site, request)
        self.failUnless('menu' in result)
        self.failUnless('required_fields' in result)
        self.failUnless('allowed_fields' in result)

    def test_submit_ok(self):
        request = testing.DummyRequest({
            'csv': self._file_upload('test_users1.csv'),
        })
        result = self._call_fut(self.site, request)

        api = result['api']
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
        self.assertEqual(profile.websites, ['http://example.com'])
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
        self.assertEqual(profile.websites, [])
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
        result = self._call_fut(self.site, request)

        api = result['api']
        self.assertEqual(api.error_message, None)
        self.assertEqual(api.status_message, "Created 1 users.")

        users = self.site.users
        self.assertEqual(users.get_by_id('user1')['password'], 'pass1234')

    def test_empty_username(self):
        request = testing.DummyRequest({
            'csv': DummyUpload(
                '"username","firstname","lastname","email","sha_password"\n'
                '"","User","One","test@example.com","pass1234"\n'
                ),
        })
        result = self._call_fut(self.site, request)

        api = result['api']
        self.assertEqual(api.error_message,
                "Malformed CSV: line 2 has an empty username.")
        self.assertEqual(api.status_message, None)

    def test_null_byte_in_row(self):
        request = testing.DummyRequest({
            'csv': DummyUpload(
                '"username","firstname","lastname","email","sha_password"\n'
                '"user1","User","One","test@example.com\x00","pass1234","foo"\n'
                ),
        })
        result = self._call_fut(self.site, request)

        api = result['api']
        self.assertEqual(api.error_message,
                         'Malformed CSV: line contains NULL byte')
        self.assertEqual(api.status_message, None)

    def test_row_too_long(self):
        request = testing.DummyRequest({
            'csv': DummyUpload(
                '"username","firstname","lastname","email","sha_password"\n'
                '"user1","User","One","test@example.com","pass1234","foo"\n'
                ),
        })
        result = self._call_fut(self.site, request)

        api = result['api']
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
        result = self._call_fut(self.site, request)

        api = result['api']
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
        result = self._call_fut(self.site, request)

        api = result['api']
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
        result = self._call_fut(self.site, request)

        api = result['api']
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
        result = self._call_fut(self.site, request)

        api = result['api']
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
        result = self._call_fut(self.site, request)

        api = result['api']
        self.assertEqual(api.error_message, None)
        self.assertEqual(api.status_message,
                          'Skipping user: user1: User already exists.\n'
                          'Created 1 users.')

    def test_skip_existing_user_in_profiles(self):
        self.site['profiles']['user1'] = testing.DummyModel(
            security_state='active')
        request = testing.DummyRequest({
            'csv': DummyUpload(
                '"username","firstname","lastname","email","password"\n'
                '"user1","User","One","test@example.com","pass1234"\n'
                '"user2","User","Two","test@example.com","pass1234"\n'
                ),
        })
        result = self._call_fut(self.site, request)

        api = result['api']
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
        result = self._call_fut(self.site, request)

        api = result['api']
        self.assertEqual(api.error_message, None)
        self.assertEqual(api.status_message,
                'Skipping user: user1: User already exists with login: user1\n'
                'Created 1 users.')

    def test_user_with_groups(self):
        # See https://bugs.launchpad.net/karl3/+bug/598246
        CSV = '\n'.join([
            '"username","firstname","lastname","email","password","groups"',
            '"user1","User","One","test@example.com","pass1234","KarlStaff"',
        ])
        request = testing.DummyRequest({
            'csv': DummyUpload(CSV),
        })
        result = self._call_fut(self.site, request)

        api = result['api']
        self.assertEqual(api.error_message, None)
        profile = self.site['profiles']['user1']
        # Groups are not attributes of the profile
        self.failIf('groups' in profile.__dict__)

    def test_user_with_utf8_attrs(self):
        # See https://bugs.launchpad.net/karl3/+bug/614398
        FIRSTNAME = u'Phr\xE9d'
        CSV = '\n'.join([
            '"username","firstname","lastname","email","password","groups"',
            '"user1","%s","","test@example.com","pass1234","KarlStaff"'
                        % FIRSTNAME.encode('utf8'),
        ])
        request = testing.DummyRequest({
            'csv': DummyUpload(CSV),
        })
        result = self._call_fut(self.site, request)

        api = result['api']
        self.assertEqual(api.error_message, None)
        profile = self.site['profiles']['user1']
        self.assertEqual(profile.firstname, FIRSTNAME)

    def test_user_with_latin1_attrs(self):
        # See https://bugs.launchpad.net/karl3/+bug/614398
        FIRSTNAME = u'Phr\xE9d'
        CSV = '\n'.join([
            '"username","firstname","lastname","email","password","groups"',
            '"user1","%s","","test@example.com","pass1234","KarlStaff"'
                        % FIRSTNAME.encode('latin1'),
        ])
        request = testing.DummyRequest({
            'csv': DummyUpload(CSV),
        })
        result = self._call_fut(self.site, request)

        api = result['api']
        self.assertEqual(api.error_message, None)
        profile = self.site['profiles']['user1']
        self.assertEqual(profile.firstname, FIRSTNAME)

    def test_blank_email(self):
        CSV = '\n'.join([
            '"username","firstname","lastname","email","password","groups"',
            '"user1","phred","","","pass1234","KarlStaff"',
        ])
        request = testing.DummyRequest({
            'csv': DummyUpload(CSV),
        })
        result = self._call_fut(self.site, request)
        api = result['api']
        self.assertEqual(api.error_message,
            'Malformed CSV: line 2 has an empty email address.')

    def test_email_matches_active_user(self):
        active_user = testing.DummyModel(security_state='active')
        active_user.__name__ = 'user0'
        self.search_results[(('email', 'foo@bar.org'),)] = (
            1, [active_user], lambda x: x)
        CSV = '\n'.join([
            '"username","firstname","lastname","email","password","groups"',
            '"user1","phred","","foo@bar.org","pass1234","KarlStaff"',
        ])
        request = testing.DummyRequest({
            'csv': DummyUpload(CSV),
        })
        result = self._call_fut(self.site, request)
        api = result['api']
        self.assertEqual(api.error_message,
            'An active user already exists with email address: foo@bar.org.')

    def test_email_matches_inactive_user(self):
        inactive_user = testing.DummyModel(security_state='inactive')
        inactive_user.__name__ = 'user0'
        self.search_results[(('email', 'foo@bar.org'),)] = (
            1, [inactive_user], lambda x: x)
        CSV = '\n'.join([
            '"username","firstname","lastname","email","password","groups"',
            '"user1","phred","","foo@bar.org","pass1234","KarlStaff"',
        ])
        request = testing.DummyRequest({
            'csv': DummyUpload(CSV),
        })
        result = self._call_fut(self.site, request)
        api = result['api']
        self.assertEqual(api.error_message,
            'A previously deactivated user exists with email address: '
            'foo@bar.org.  Consider checking the "Reactivate user" checkbox '
            'to reactivate the user.')

    def test_email_matches_inactive_user_reactivate(self):
        renamed_users = []
        def rename_user(context, old_name, new_name, merge, out):
            print >>out, 'Line 1.'
            print >>out, 'Line 2.'
            renamed_users.append((old_name, new_name))
            self.failUnless(merge)

        inactive_user = testing.DummyModel(security_state='inactive')
        inactive_user.__name__ = 'user0'
        self.search_results[(('email', 'foo@bar.org'),)] = (
            1, [inactive_user], lambda x: x)
        CSV = '\n'.join([
            '"username","firstname","lastname","email","password","groups"',
            '"user1","phred","","foo@bar.org","pass1234","KarlStaff"',
        ])
        request = testing.DummyRequest({
            'csv': DummyUpload(CSV),
            'reactivate': 'true',
        })
        result = self._call_fut(self.site, request, rename_user)
        api = result['api']
        self.assertEqual(api.error_message, None)
        self.assertEqual(api.status_message,
                         'Line 1.\nLine 2.\n\nCreated 1 users.')
        self.assertEqual(renamed_users, [('user0', 'user1')])

    def test_reactivate_user(self):
        inactive_user = testing.DummyModel(security_state='inactive')
        inactive_user.__name__ = 'user1'
        self.search_results[(('email', 'foo@bar.org'),)] = (
            1, [inactive_user], lambda x: x)
        self.site['profiles']['user1'] = inactive_user
        CSV = '\n'.join([
            '"username","firstname","lastname","email","password","groups"',
            '"user1","phred","","foo@bar.org","pass1234","KarlStaff"',
        ])
        request = testing.DummyRequest({
            'csv': DummyUpload(CSV),
            'reactivate': 'true',
        })
        result = self._call_fut(self.site, request)
        api = result['api']
        self.assertEqual(api.error_message, None)
        self.assertEqual(api.status_message,
                         'Reactivated user1.\nCreated 1 users.')
        self.assertEqual(self.workflow.transitioned[0]['to_state'], 'active')

class TestPostofficeQuarantineView(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

        from karl.views import admin
        self.queue = DummyPostofficeQueue()
        admin.open_queue = self.queue

        from pyramid.interfaces import ISettings
        karltesting.registerUtility(
            karltesting.DummySettings(**{
                'postoffice.zodb_uri': 'zeo://localhost:9002',
                'postoffice.queue': 'queue'}), ISettings
        )
        karltesting.registerDummyRenderer('karl.views:templates/admin/menu.pt')

    def tearDown(self):
        testing.cleanUp()

    def _call_fut(self, params=None):
        from karl.views.admin import postoffice_quarantine_view as fut
        if params is None:
            params = {}
        request = testing.DummyRequest(params=params)
        request.view_name = 'view'
        request.context = DummyModel()
        request.context._p_jar = mock.Mock()
        request.context._p_jar.db.return_value.databases = {
            'postoffice': 'dummy'}
        return fut(request)

    def test_it(self):
        messages = self._call_fut()['messages']
        self.assertEqual(len(messages), 2)

        message = messages.pop(0)
        self.assertEqual(message['url'], 'http://example.com/po_quarantine/0')
        self.assertEqual(message['message_id'], 'Message 1')
        self.assertEqual(message['po_id'], '0')
        self.assertEqual(unicode(message['error']), u'Error 1')

        message = messages.pop(0)
        self.assertEqual(message['url'], 'http://example.com/po_quarantine/1')
        self.assertEqual(message['message_id'], 'Message 2')
        self.assertEqual(message['po_id'], '1')
        self.assertEqual(unicode(message['error']), u'Error\xa02')

    def test_requeue_message(self):
        response = self._call_fut(params={'requeue_0': 1})
        self.assertEqual(response.location, 'http://example.com/view')
        self.assertEqual(self.queue.removed, ['Message 1'])
        self.assertEqual(self.queue.added, ['Message 1'])
        self.failUnless(self.queue.committed)

    def test_requeue_all(self):
        response = self._call_fut(params={'requeue_all': 1})
        self.assertEqual(response.location, 'http://example.com/view')
        self.assertEqual(self.queue.removed, ['Message 1', 'Message 2'])
        self.assertEqual(self.queue.added, ['Message 1', 'Message 2'])
        self.failUnless(self.queue.committed)

    def test_delete_message(self):
        response = self._call_fut(params={'delete_1': 1})
        self.assertEqual(response.location, 'http://example.com/view')
        self.assertEqual(self.queue.removed, ['Message 2'])
        self.assertEqual(self.queue.added, [])
        self.failUnless(self.queue.committed)

    def test_delete_all(self):
        response = self._call_fut(params={'delete_all': 1})
        self.assertEqual(response.location, 'http://example.com/view')
        self.assertEqual(self.queue.removed, ['Message 1', 'Message 2'])
        self.assertEqual(self.queue.added, [])
        self.failUnless(self.queue.committed)

class TestPostOfficeQuarantineStatusView(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

        from karl.views import admin
        self.queue = DummyPostofficeQueue()
        admin.open_queue = self.queue

        from pyramid.interfaces import ISettings
        karltesting.registerUtility(
            karltesting.DummySettings(**{
                'postoffice.zodb_uri': 'zeo://localhost:9002',
                'postoffice.queue': 'queue'}), ISettings
        )

    def tearDown(self):
        testing.cleanUp()

    def _call_fut(self, id='0'):
        from karl.views.admin import postoffice_quarantine_status_view as fut
        request = testing.DummyRequest()
        request.context = mock.Mock()
        request.context._p_jar.db.return_value.databases = {
            'postoffice': 'dummy'}
        return fut(request)

    def test_error(self):
        self.assertEqual(self._call_fut().body, 'ERROR')

    def test_ok(self):
        self.queue._msgs = []
        self.assertEqual(self._call_fut().body, 'OK')

class TestPostofficeQuarantinedMessageView(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

        from karl.views import admin
        self.queue = DummyPostofficeQueue()
        admin.open_queue = self.queue

        from pyramid.interfaces import ISettings
        karltesting.registerUtility(
            karltesting.DummySettings(**{
                'postoffice.zodb_uri': 'zeo://localhost:9002',
                'postoffice.queue': 'queue'}), ISettings
        )

    def tearDown(self):
        testing.cleanUp()

    def _call_fut(self, id='0'):
        from karl.views.admin import postoffice_quarantined_message_view as fut
        request = testing.DummyRequest()
        request.context = mock.Mock()
        request.context._p_jar.db.return_value.databases = {
            'postoffice': 'dummy'}
        request.matchdict = {'id': id}
        return fut(request)

    def test_it(self):
        self.assertEqual(
            self._call_fut().body, 'An urgent message for Obi Wan.'
        )

    def test_notfound(self):
        from pyramid.exceptions import NotFound
        self.assertRaises(NotFound, self._call_fut, 2)

class Test_rename_or_merge_user_view(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()
        self.rename_user_calls = []

    def tearDown(self):
        testing.cleanUp()

    def _dummy_rename_user(self, context, old_name, new_name, merge, out):
        print >>out, 'Renamed user.'
        self.rename_user_calls.append((context, old_name, new_name, merge))

    def _call_fut(self, request, rename_user=None):
        if rename_user is None:
            rename_user = self._dummy_rename_user

        from karl.views.admin import rename_or_merge_user_view as fut
        return fut(request, rename_user=rename_user)

    def test_show_form(self):
        request = testing.DummyRequest()
        request.context = testing.DummyModel()
        response = self._call_fut(request)
        self.failUnless('api' in response)
        self.failUnless('menu' in response)
        api = response['api']
        self.failIf(api.error_message)
        self.failIf(api.status_message)

    def test_rename_user(self):
        request = testing.DummyRequest(
            params={
            'old_username': 'harry',
            'new_username': 'henry'
            },
        )
        request.context = testing.DummyModel()

        response = self._call_fut(request)
        self.assertEqual(
            self.rename_user_calls,
            [(request.context, 'harry', 'henry', False)]
        )
        api = response['api']
        self.failIf(api.error_message)
        self.assertEqual(api.status_message, 'Renamed user.\n')

    def test_merge_user(self):
        request = testing.DummyRequest(
            params={
            'old_username': 'harry',
            'new_username': 'henry',
            'merge': '1',
            },
        )
        request.context = testing.DummyModel()

        response = self._call_fut(request)
        self.assertEqual(
            self.rename_user_calls,
            [(request.context, 'harry', 'henry', True)]
        )
        api = response['api']
        self.failIf(api.error_message)
        self.assertEqual(api.status_message, 'Renamed user.\n')

    def test_error_in_rename_user(self):
        request = testing.DummyRequest(
            params={
            'old_username': 'harry',
            'new_username': 'henry',
            'merge': '1',
            },
        )
        request.context = testing.DummyModel()
        def rename_user(*args, **kw):
            raise ValueError("You're doing it wrong.")

        response = self._call_fut(request, rename_user=rename_user)
        api = response['api']
        self.assertEqual(api.error_message, "You're doing it wrong.")
        self.failIf(api.status_message)

class DummyProfiles(testing.DummyModel):

    def __setitem__(self, name, other):
        if not name:
            raise TypeError("Name must not be empty")
        return testing.DummyModel.__setitem__(self, name, other)

class DummyPostofficeQueue(object):
    _msgs = [
        ({'Message-Id': "Message 1",
          'X-Postoffice-Id': '0',
          'body': 'An urgent message for Obi Wan.'}, "Error 1"),
        ({'Message-Id': "Message 2",
          'X-Postoffice-Id': '1',
          'body': 'Help me Obi Wan Kenobi.'}, u"Error\xa02".encode('UTF8')),
    ]

    def __init__(self):
        self.removed = []
        self.added = []
        self.committed = False

    def __call__(self, db, queue_name):
        self.db = db
        self.queue_name = queue_name
        class DummyCloser(object):
            @property
            def conn(myself):
                return myself
            @property
            def transaction_manager(myself):
                return myself
            def commit(myself):
                self.committed = True

        return self, DummyCloser()

    def get_quarantined_messages(self):
        for msg in self._msgs:
            yield msg

    def get_quarantined_message(self, id):
        if int(id) >= len(self._msgs):
            raise KeyError(id)
        return DummyMessage(self._msgs[int(id)][0])

    def remove_from_quarantine(self, message):
        self.removed.append(message['Message-Id'])

    def add(self, message):
        self.added.append(message['Message-Id'])

    def count_quarantined_messages(self):
        return len(self._msgs)

class DummyMessage(dict):
    def __init__(self, d):
        self.update(d)

    def as_string(self):
        return self['body']

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
