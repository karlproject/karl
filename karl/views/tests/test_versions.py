import mock
import unittest
from pyramid import testing

import karl.testing


class Test_show_history(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        from karl.views.versions import show_history
        return show_history(context, request, tz=5 * 3600)

    def test_it(self):
        from datetime import datetime
        request = testing.DummyRequest()
        context = testing.DummyModel(
            docid=3,
            title='Title',
        )
        context['profiles'] = profiles = testing.DummyModel()
        profiles['ed'] = testing.DummyModel(title='Ed')
        context.repo = DummyArchive([
            Dummy(
                docid=2,
                user='ed',
                archive_time=datetime(2010, 5, 13, 2, 42),
                version_num=2,
                current_version=2,
            ),
            Dummy(
                docid=1,
                user='ed',
                archive_time=datetime(2010, 5, 12, 2, 42),
                version_num=1,
                current_version=2,
            ),
        ])
        result = self._callFUT(context, request)
        history = result['history']
        self.assertEqual(len(history), 2)
        self.assertEqual(len(history[0]), 5)
        self.assertEqual(history[0]['date'], '2010-05-12 21:42')
        self.assertEqual(history[0]['editor'], {
            'name': 'Ed', 'url': 'http://example.com/profiles/ed/'})
        self.assertEqual(history[0]['preview_url'],
                         'http://example.com/preview.html?version_num=2')
        self.assertEqual(history[0]['restore_url'],
                         'http://example.com/revert?version_num=2')
        self.assertEqual(history[0]['is_current'], True)
        self.assertEqual(len(history[1]), 5)
        self.assertEqual(history[1]['date'], '2010-05-11 21:42')
        self.assertEqual(history[1]['editor'], {
            'name': 'Ed', 'url': 'http://example.com/profiles/ed/'})
        self.assertEqual(history[1]['preview_url'],
                         'http://example.com/preview.html?version_num=1')
        self.assertEqual(history[1]['restore_url'],
                         'http://example.com/revert?version_num=1')
        self.assertEqual(history[1]['is_current'], False)


class Test_revert(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        from karl.views.versions import revert
        return revert(context, request)

    def test_it(self):
        request = testing.DummyRequest(params={
            'version_num': '1',
        })
        context = testing.DummyModel(
            docid=3,
            title='Title',
        )
        context['profiles'] = profiles = testing.DummyModel()
        profiles['ed'] = testing.DummyModel(title='Ed')
        context.repo = DummyArchive([
            Dummy(version_num=1, docid=1),
            Dummy(version_num=2, docid=2),
        ])
        context.catalog = DummyCatalog()
        reverted = []
        def dummy_revert(version):
            reverted.append(version)
        context.revert = dummy_revert
        result = self._callFUT(context, request)
        self.assertEqual(result.location, 'http://example.com/')
        self.assertEqual(len(reverted), 1)
        self.assertEqual(reverted[0].version_num, 1)
        self.assertEqual(context.repo._reverted, [(3, 1)])
        self.assertEqual(context.catalog.reindexed, [(3, context)])

    def test_it_no_such_version(self):
        request = testing.DummyRequest(params={
            'version_num': '5',
        })
        context = testing.DummyModel(
            docid=3,
            title='Title',
        )
        context['profiles'] = profiles = testing.DummyModel()
        profiles['ed'] = testing.DummyModel(title='Ed')
        context.repo = DummyArchive([
            Dummy(version_num=1, docid=1),
            Dummy(version_num=2, docid=2),
        ])
        self.assertRaises(ValueError, self._callFUT, context, request)


class Test_show_trash(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        request.layout_manager = mock.Mock()
        layout = request.layout_manager.layout
        layout.page_title = 'Trash'
        from karl.views.versions import show_trash
        return show_trash(context, request, tz=5 * 3600)

    def test_shallow(self):
        from datetime import datetime
        request = testing.DummyRequest()
        context = testing.DummyModel(
            docid=0,
            title='Title',
            map={},
        )
        context['profiles'] = profiles = testing.DummyModel()
        profiles['ed'] = testing.DummyModel(title='Ed')
        deleted =  [
            Dummy(
                deleted_by='ed',
                deleted_time=datetime(2010, 5, 12, 2, 42),
                docid=1,
                name="foo1",
                title="Title 1",
                new_container_ids=[6],
            ),
            Dummy(
                deleted_by='ed',
                deleted_time=datetime(2010, 5, 12, 2, 42),
                docid=2,
                name="foo2",
                title="Title 2",
                new_container_ids=[],
            ),
            Dummy(
                deleted_by='ed',
                deleted_time=datetime(2010, 5, 13, 2, 42),
                docid=3,
                name="foo3",
                title="Title 3",
                new_container_ids=[],
            )]

        context.repo = DummyArchive(
            [Dummy(docid=0, deleted=deleted, map={})] + deleted)

        result = self._callFUT(context, request)
        history = result['deleted']
        self.assertEqual(len(history), 2)
        self.assertEqual(len(history[0]), 5)
        self.assertEqual(history[0]['date'], '2010-05-11 21:42')
        self.assertEqual(history[0]['deleted_by'], {
            'name': 'Ed', 'url': 'http://example.com/profiles/ed/'})
        self.assertEqual(history[0]['restore_url'],
                         'http://example.com/restore?docid=2&name=foo2')
        self.assertEqual(history[0]['title'], 'Title 2')
        self.assertEqual(history[0]['url'], None)
        self.assertEqual(len(history[1]), 5)
        self.assertEqual(history[1]['date'], '2010-05-12 21:42')
        self.assertEqual(history[1]['deleted_by'], {
            'name': 'Ed', 'url': 'http://example.com/profiles/ed/'})
        self.assertEqual(history[1]['restore_url'],
                         'http://example.com/restore?docid=3&name=foo3')
        self.assertEqual(history[1]['title'], 'Title 3')
        self.assertEqual(history[0]['url'], None)

    def test_file_deleted_in_subfolder(self):
        from datetime import datetime
        request = testing.DummyRequest()
        context = testing.DummyModel(
            docid=0,
            title='Title',
            map={},
        )
        context['profiles'] = profiles = testing.DummyModel()
        profiles['ed'] = testing.DummyModel(title='Ed')
        deleted_item =  Dummy(
            deleted_by='ed',
            deleted_time=datetime(2010, 5, 12, 2, 42),
            docid=1,
            name="foo1",
            title="Title 1",
            new_container_ids=[])

        context.repo = DummyArchive([
            Dummy(docid=0, deleted=[], map={'parent': 2},
                  new_container_ids=[]),
            Dummy(docid=2, deleted=[deleted_item], map={},
                  new_container_ids=[], title='Parent'),
            deleted_item,
        ])

        # Show top level
        result = self._callFUT(context, request)
        history = result['deleted']
        self.assertEqual(len(history), 1)
        self.assertEqual(len(history[0]), 5)
        self.assertEqual(history[0]['date'], None)
        self.assertEqual(history[0]['deleted_by'], None)
        self.assertEqual(history[0]['restore_url'], None)
        self.assertEqual(history[0]['title'], 'Parent')
        self.assertEqual(history[0]['url'],
                         'http://example.com/trash?subfolder=2')

        # Show second level
        request.params['subfolder'] = '2'
        result = self._callFUT(context, request)
        history = result['deleted']
        self.assertEqual(len(history), 1)
        self.assertEqual(len(history[0]), 5)
        self.assertEqual(history[0]['date'], '2010-05-11 21:42')
        self.assertEqual(history[0]['deleted_by'], {
            'name': 'Ed', 'url': 'http://example.com/profiles/ed/'})
        self.assertEqual(history[0]['restore_url'],
                         'http://example.com/restore?docid=1&name=foo1')
        self.assertEqual(history[0]['title'], 'Title 1')
        self.assertEqual(history[0]['url'], None)

    def test_it_container_not_in_repo(self):
        request = testing.DummyRequest()
        context = testing.DummyModel(
            docid=3,
            title='Title',
        )
        context.repo = DummyArchive([])
        result = self._callFUT(context, request)
        history = result['deleted']
        self.assertEqual(len(history), 0)


class Test_undelete(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

        from zope.interface import Interface
        from karl.models.interfaces import IContainerVersion
        karl.testing.registerAdapter(DummyAdapter, Interface, IContainerVersion)

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        from karl.views.versions import undelete
        return undelete(context, request)

    def _make_repo(self, context):
        from datetime import datetime
        deleted_child = Dummy(
            klass=DummyModel,
            docid=3,
            name='child',
            new_container_ids=[])
        deleted_item = Dummy(
            klass=DummyModel,
            deleted_by='ed',
            deleted_time=datetime(2010, 5, 12, 2, 42),
            docid=2,
            name="foo2",
            title="Title 2",
            new_container_ids=[],
            map={'child': 3},
            deleted=[],
        )
        context.repo = DummyArchive([
            deleted_item,
            deleted_child,
            Dummy(
                klass=DummyModel,
                deleted_by='ed',
                deleted_time=datetime(2010, 5, 13, 2, 42),
                docid=33,
                name="foo3",
                title="Title 3",
                map={},
                deleted=[deleted_item]),
        ])

    def test_non_conflicting_name(self):
        request = testing.DummyRequest({
            'docid': 2, 'name': 'foo2'
        })
        context = DummyModel(
            docid=33,
            title='Title',
        )
        context['profiles'] = profiles = testing.DummyModel()
        profiles['ed'] = testing.DummyModel(title='Ed')
        self._make_repo(context)
        result = self._callFUT(context, request)
        self.assertEqual(result.location, 'http://example.com/')
        self.assertEqual(context['foo2'].reverted[0].docid, 2)
        self.assertEqual(len(context['foo2'].reverted), 1)
        self.assertEqual(context['foo2']['child'].reverted[0].docid, 3)
        self.assertEqual(len(context['foo2']['child'].reverted), 1)
        self.assertEqual(context.repo.containers, [(context, None)])

    def test_conflicting_name(self):
        request = testing.DummyRequest({
            'docid': 2, 'name': 'foo2'
        })
        context = DummyModel(
            docid=33,
            title='Title',
        )
        context['foo2'] = DummyModel()
        context['profiles'] = profiles = testing.DummyModel()
        profiles['ed'] = testing.DummyModel(title='Ed')
        self._make_repo(context)
        result = self._callFUT(context, request)
        self.assertEqual(result.location, 'http://example.com/')
        self.assertEqual(context['foo2-1'].reverted[0].docid, 2)
        self.assertEqual(len(context['foo2-1'].reverted), 1)
        self.assertEqual(context['foo2-1']['child'].reverted[0].docid, 3)
        self.assertEqual(len(context['foo2-1']['child'].reverted), 1)
        self.assertEqual(context.repo.containers, [(context, None)])

    def test_restore_file_to_subfolder(self):
        from datetime import datetime
        context = DummyModel(docid=1, title='The Context')
        context['folder'] = DummyModel(docid=2, title='The Folder')
        deleted_item = Dummy(
            klass=DummyModel,
            deleted_by='ed',
            deleted_time=datetime(2010, 5, 12, 2, 42),
            docid=3,
            name="doc",
            title="The Document",
            new_container_ids=[],
        )
        context.repo = DummyArchive([
            deleted_item,
            Dummy(
                klass=DummyModel,
                docid=1,
                name="context",
                title="The Context",
                new_container_ids=[],
                map={'folder': 2},
                deleted=[]),
            Dummy(
                klass=DummyModel,
                docid=2,
                name='folder',
                title='The Folder',
                new_container_ids=[],
                map={},
                deleted=[deleted_item])])
        request = testing.DummyRequest({
            'docid': 3, 'name': 'doc'
        })
        result = self._callFUT(context, request)
        self.assertEqual(result.location, 'http://example.com/folder/')
        self.assertEqual(context['folder']['doc'].reverted[0].docid, 3)

    def test_restore_file_in_deleted_subfolder(self):
        from datetime import datetime
        context = DummyModel(docid=1, title='The Context')
        deleted_item = Dummy(
            klass=DummyModel,
            deleted_by='ed',
            deleted_time=datetime(2010, 5, 12, 2, 42),
            docid=3,
            name="doc",
            title="The Document",
            new_container_ids=[],
        )
        deleted_subfolder = Dummy(
            klass=DummyModel,
            deleted_by='ed',
            deleted_time=datetime(2010, 5, 12, 2, 42),
            docid=2,
            name="folder",
            title="The Folder",
            new_container_ids=[],
            map={'doc': 3},
            deleted=[])
        context.repo = DummyArchive([
            deleted_item,
            deleted_subfolder,
            Dummy(
                klass=DummyModel,
                docid=1,
                name="context",
                title="The Context",
                new_container_ids=[],
                map={'folder': 2},
                deleted=[deleted_subfolder])])

        request = testing.DummyRequest({
            'docid': 3, 'name': 'doc'
        })
        result = self._callFUT(context, request)
        self.assertEqual(result.location, 'http://example.com/folder/')
        self.assertEqual(context['folder'].reverted[0].docid, 2)
        self.assertEqual(context['folder']['doc'].reverted[0].docid, 3)

class Test_show_history_lock(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _callFUT(self, context, request):
        from karl.views.versions import show_history
        return show_history(context, request)

    def test_show_locked_page(self):
        from karl.testing import DummyRoot
        site = DummyRoot()
        context = testing.DummyModel(title='title', docid=1)
        site.repo = DummyArchive([])
        site['foo'] = context

        import datetime
        lock_time = datetime.datetime.now() - datetime.timedelta(seconds=1)
        context.lock = {'time': lock_time,
                        'userid': 'foo'}

        request = testing.DummyRequest()
        response = self._callFUT(context, request)
        self.failUnless(response['lock_info']['is_locked'])


class Test_format_local_date(unittest.TestCase):

    def _callFUT(self, date, tz=None, time_module=None):
        if time_module is None:
            import time
            time_module = time
        from karl.views.versions import format_local_date
        return format_local_date(date, tz=tz, time_module=time_module)

    def test_with_tz_specified(self):
        import datetime
        dt = datetime.datetime(2011, 8, 30, 7, 30, 15)
        s = self._callFUT(dt, 7 * 3600)
        self.assertEqual(s, '2011-08-30 00:30')

    def _make_time_module(self, daylight=0, isdst=False):
        # Make an object simulates the time module.

        class TimeModule:
            timezone = 6 * 3600
            altzone = 7 * 3600

            def __init__(self):
                self.daylight = daylight

            def localtime(self, t):
                class struct_time:
                    tm_isdst = isdst

                return struct_time()

        return TimeModule()

    def test_in_zone_without_daylight_savings(self):
        import datetime
        dt = datetime.datetime(2011, 8, 30, 7, 30, 15)
        s = self._callFUT(dt, time_module=self._make_time_module(daylight=0))
        self.assertEqual(s, '2011-08-30 01:30')

    def test_with_daylight_savings_in_effect(self):
        import datetime
        dt = datetime.datetime(2011, 8, 30, 7, 30, 15)
        s = self._callFUT(dt,
            time_module=self._make_time_module(daylight=1, isdst=True))
        self.assertEqual(s, '2011-08-30 00:30')

    def test_with_daylight_savings_not_in_effect(self):
        import datetime
        dt = datetime.datetime(2011, 1, 30, 7, 30, 15)
        s = self._callFUT(dt,
            time_module=self._make_time_module(daylight=1, isdst=False))
        self.assertEqual(s, '2011-01-30 01:30')


class DummyArchive(object):

    def __init__(self, history):
        self._history = history
        self._docs = dict([(doc.docid, doc) for doc in history])
        self._reverted = []
        self.containers = []

    def history(self, docid, only_current=False):
        if only_current:
            for version in self._history:
                if version.docid == docid:
                    return [version]
            else:
                raise KeyError(docid)
        return self._history

    def reverted(self, docid, version_num):
        self._reverted.append((docid, version_num))

    def container_contents(self, docid):
        contents = self._docs.get(docid)
        if contents is None or not hasattr(contents, 'map'):
            from sqlalchemy.orm.exc import NoResultFound
            raise NoResultFound
        return contents

    def archive_container(self, container, user):
        self.containers.append((container, user))


class Dummy(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)


class DummyModel(testing.DummyModel):
    def __init__(self, **kw):
        testing.DummyModel.__init__(self, **kw)
        self.reverted = []

    def add(self, name, value, send_events=True):
        self[name] = value

    def revert(self, version):
        self.reverted.append(version)

def DummyAdapter(obj):
    return obj

class DummyCatalog(object):

    def __init__(self):
        self.reindexed = []

    def reindex_doc(self, docid, doc):
        self.reindexed.append((docid, doc))
