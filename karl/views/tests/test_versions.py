
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


class TestShowTrash(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _make(self, context, request):
        from karl.views.versions import ShowTrash
        return ShowTrash(context, request, tz=5 * 3600)

    def _make_context(self):
        from datetime import datetime
        context = testing.DummyModel(
            docid=2,
            title='Top 2',
        )
        context['child'] = testing.DummyModel(
            docid=3,
            title='Child 3',
        )
        context['child']['grandchild4'] = testing.DummyModel(
            docid=4,
            title='Grand 4',
        )
        context['doc'] = testing.DummyModel(
            docid=8,
            title='Document 8',
        )

        self.deleted_grandchild = Dummy(
            deleted_by='ed',
            deleted_time=datetime(2010, 5, 12, 2, 42),
            docid=5,
            name="grandchild5",
            title="Grand 5",
            new_container_ids=[],
        )
        self.moved_grandchild = Dummy(
            deleted_by='ed',
            deleted_time=datetime(2010, 5, 12, 2, 42),
            docid=6,
            name="grandchild6",
            title="Grand 6",
            new_container_ids=[5],
        )
        context.repo = DummyArchive(
            [
                Dummy(docid=2,
                    title="Top 2 (archived)",
                    deleted=[],
                    map={'child': 3, 'doc': 8},
                ),
                Dummy(docid=3,
                    title="Child 3 (archived)",
                    deleted=[self.deleted_grandchild, self.moved_grandchild],
                    map={'grandchild4': 4},
                ),
                Dummy(docid=4,
                    title="Grand 4 (archived)",
                    deleted=[],
                    map={},
                ),
                Dummy(docid=5,
                    title="Grand 5 (archived)",
                    deleted=[],
                    map={'grandchild6': 6},
                ),
                Dummy(docid=6, title="Grand 6 (archived)", deleted=[]),
                Dummy(docid=8, title="Document 8 (archived)", deleted=[]),
            ],
            contain_deleted=[2, 3],
        )
        context['profiles'] = self.profiles = testing.DummyModel()
        self.profiles['ed'] = testing.DummyModel(
            title='Mr. Ed',
        )
        return context

    def test_ctor_without_subfolder(self):
        request = testing.DummyRequest()
        context = self._make_context()
        view = self._make(context, request)
        self.assertEqual(view.deleted_branch, None)
        self.assertEqual(view.container_id, 2)
        self.assertEqual(view.error, None)
        self.assertEqual(view.deleted, [])
        self.assertEqual(view.subfolder_path, [])

    def test_ctor_with_valid_subfolder(self):
        request = testing.DummyRequest({
            'subfolder': '{3}child/{4}grandchild4'})
        context = self._make_context()
        view = self._make(context, request)
        self.assertEqual(view.deleted_branch, None)
        self.assertEqual(view.container_id, 4)
        self.assertEqual(view.error, None)
        self.assertEqual(view.deleted, [])
        self.assertEqual(view.subfolder_path,
            [(u'child', 3), (u'grandchild4', 4)])

    def test_ctor_with_implicit_subfolder(self):
        request = testing.DummyRequest({
            'subfolder': 'child/grandchild4'})
        context = self._make_context()
        view = self._make(context, request)
        self.assertEqual(view.deleted_branch, None)
        self.assertEqual(view.container_id, 4)
        self.assertEqual(view.error, None)
        self.assertEqual(view.deleted, [])
        self.assertEqual(view.subfolder_path,
            [(u'child', 3), (u'grandchild4', 4)])

    def test_ctor_with_traversal_through_deleted_subfolder(self):
        request = testing.DummyRequest({
            'subfolder': '{3}child/{5}grandchild5'})
        context = self._make_context()
        view = self._make(context, request)
        self.assertEqual(view.deleted_branch, self.deleted_grandchild)
        self.assertEqual(view.container_id, 5)
        self.assertEqual(view.error, None)
        self.assertEqual(view.deleted, [])
        self.assertEqual(view.subfolder_path,
            [(u'child', 3), (u'grandchild5', 5)])

    def test_ctor_with_traversal_through_moved_subfolder(self):
        request = testing.DummyRequest({
            'subfolder': '{3}child/{6}grandchild6'})
        context = self._make_context()
        view = self._make(context, request)
        self.assertEqual(view.deleted_branch, None)
        self.assertEqual(view.container_id, 3)
        self.assertTrue(isinstance(view.error, ValueError), view.error)
        self.assertEqual(view.deleted, [])
        self.assertEqual(view.subfolder_path, [(u'child', 3)])

    def test_ctor_with_traversal_through_non_container(self):
        request = testing.DummyRequest({
            'subfolder': '{8}doc/{3}child'})
        context = self._make_context()
        view = self._make(context, request)
        self.assertEqual(view.deleted_branch, None)
        self.assertEqual(view.container_id, 8)
        self.assertTrue(isinstance(view.error, ValueError), view.error)
        self.assertEqual(view.deleted, [])
        self.assertEqual(view.subfolder_path, [(u'doc', 8)])

    def test_call_without_subfolder(self):
        request = testing.DummyRequest()
        context = self._make_context()
        view = self._make(context, request)
        d = view()
        self.assertEqual(d['api'].get_status_message(), None)
        self.maxDiff = 10000
        self.assertEqual(d['deleted'], [{
            'date': None,
            'deleted_by': None,
            'restore_url': None,
            'title': 'Child 3 (archived)',
            'url': 'http://example.com/trash?subfolder=%7B3%7Dchild',
        }])

    def test_call_with_existing_subfolder(self):
        request = testing.DummyRequest({
            'subfolder': '{3}child'})
        context = self._make_context()
        view = self._make(context, request)
        d = view()
        self.assertEqual(d['api'].get_status_message(), None)
        self.maxDiff = 10000
        self.assertEqual(d['deleted'], [{
            'date': '2010-05-11 21:42',
            'deleted_by': {
                'name': 'Mr. Ed',
                'url': 'http://example.com/profiles/ed/',
            },
            'restore_url':
                'http://example.com/restore?'
                'path=%7B3%7Dchild%2F%7B5%7Dgrandchild5',
            'title': 'Grand 5 (archived)',
            'url':
                'http://example.com/trash?'
                'subfolder=%7B3%7Dchild%2F%7B5%7Dgrandchild5',
        }])

    def test_call_with_deleted_subfolder(self):
        request = testing.DummyRequest({
            'subfolder': '{3}child/{5}grandchild5'})
        context = self._make_context()
        view = self._make(context, request)
        d = view()
        self.assertEqual(d['api'].get_status_message(), None)
        self.maxDiff = 10000
        self.assertEqual(d['deleted'], [{
            'date': '2010-05-11 21:42',
            'deleted_by': {
                'name': 'Mr. Ed',
                'url': 'http://example.com/profiles/ed/',
            },
            'restore_url': 'http://example.com/restore?path='
                '%7B3%7Dchild%2F%7B5%7Dgrandchild5%2F%7B6%7Dgrandchild6',
            'title': 'Grand 6 (archived)',
            'url': None
        }])

    def test_call_with_bogus_subfolder(self):
        request = testing.DummyRequest({
            'subfolder': '{99}x'})
        context = self._make_context()
        view = self._make(context, request)
        d = view()
        self.assertEqual(d['api'].get_status_message(),
            "Subfolder not found in trash: x (docid 99)")
        self.maxDiff = 10000
        self.assertEqual(d['deleted'], [])


class Test_undelete(unittest.TestCase):

    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()

    def _call(self, context, request):
        from karl.views.versions import undelete
        return undelete(context, request)

    def _register_adapter(self):
        from zope.interface import Interface
        from karl.models.interfaces import IContainerVersion
        karl.testing.registerAdapter(
            DummyAdapter, Interface, IContainerVersion)

    def _make_context(self):
        class VersionedDummyModel(testing.DummyModel):
            def __init__(self, **kw):
                testing.DummyModel.__init__(self, **kw)
                self.reverted = []

            def add(self, name, value, send_events=True):
                value.__parent__ = self
                value.__name__ = name
                self[name] = value

            def revert(self, version):
                self.reverted.append(version)
                self.docid = version.docid

        context = VersionedDummyModel(
            docid=2,
            title='Top 2',
        )
        context['child'] = VersionedDummyModel(
            __parent__=context,
            __name__='child',
            docid=3,
            title='Child 3',
        )

        self.deleted_grandchild = Dummy(
            docid=5,
            name="grandchild5",
            title="Grand 5",
            new_container_ids=[],
        )
        context.repo = DummyArchive(
            [
                Dummy(docid=2,
                    title="Top 2 (archived)",
                    deleted=[],
                    map={'child': 3, 'doc': 7},
                ),
                Dummy(docid=3,
                    title="Child 3 (archived)",
                    deleted=[self.deleted_grandchild],
                    map={'grandchild4': 4},
                ),
                Dummy(docid=5,
                    title="Grand 5 (archived)",
                    deleted=[],
                    map={'grandchild6': 6},
                    klass=VersionedDummyModel,
                ),
                Dummy(
                    docid=6,
                    title="Grand 6 (archived)",
                    deleted=[],
                    klass=VersionedDummyModel,
                ),
                Dummy(
                    docid=7,
                    title="Document 7 (archived)",
                    deleted=[],
                    klass=VersionedDummyModel,
                ),
            ],
        )
        return context

    def test_restore_document_with_non_conflicting_name(self):
        self._register_adapter()
        request = testing.DummyRequest({
            'path': '{7}doc',
        })
        context = self._make_context()
        result = self._call(context, request)
        self.assertEqual(
            result.location, 'http://example.com/doc/')
        self.assertEqual(len(context.reverted), 0)
        self.assertEqual(len(context['doc'].reverted), 1)
        self.assertEqual(context['doc'].reverted[0].docid, 7)
        self.assertEqual(context.repo.containers, [
            (context, None),
        ])

    def test_restore_document_with_conflicting_name(self):
        self._register_adapter()
        request = testing.DummyRequest({
            'path': '{7}doc',
        })
        context = self._make_context()
        context['doc'] = testing.DummyModel(
            docid=8,
            title='Document 8',
        )
        result = self._call(context, request)
        self.assertEqual(
            result.location, 'http://example.com/doc-1/')
        self.assertEqual(len(context.reverted), 0)
        self.assertEqual(len(context['doc-1'].reverted), 1)
        self.assertEqual(context['doc-1'].reverted[0].docid, 7)
        self.assertEqual(context.repo.containers, [
            (context, None),
        ])

    def test_restore_ancestors_of_undeleted_object(self):
        self._register_adapter()
        request = testing.DummyRequest({
            'path': '{3}child/{5}grandchild5/{6}grandchild6',
        })
        context = self._make_context()
        result = self._call(context, request)
        self.assertEqual(
            result.location,
            'http://example.com/child/grandchild5/grandchild6/')
        self.assertEqual(len(context.reverted), 0)
        self.assertEqual(len(context['child'].reverted), 0)

        gc5 = context['child']['grandchild5']
        self.assertEqual(gc5.reverted[0].docid, 5)
        self.assertEqual(len(gc5.reverted), 1)
        self.assertEqual(gc5['grandchild6'].reverted[0].docid, 6)
        self.assertEqual(len(gc5['grandchild6'].reverted), 1)
        self.assertEqual(context.repo.containers, [
            (context['child'], None),
            (gc5, None),
        ])

    def test_restore_descendants_of_undeleted_object(self):
        self._register_adapter()
        request = testing.DummyRequest({
            'path': '{3}child/{5}grandchild5',
        })
        context = self._make_context()
        result = self._call(context, request)
        self.assertEqual(
            result.location, 'http://example.com/child/grandchild5/')
        self.assertEqual(len(context.reverted), 0)
        self.assertEqual(len(context['child'].reverted), 0)

        gc5 = context['child']['grandchild5']
        self.assertEqual(gc5.reverted[0].docid, 5)
        self.assertEqual(len(gc5.reverted), 1)
        self.assertEqual(gc5['grandchild6'].reverted[0].docid, 6)
        self.assertEqual(len(gc5['grandchild6'].reverted), 1)
        self.assertEqual(context.repo.containers, [
            (context['child'], None),
            (gc5, None),
        ])


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
        # Make an object that simulates the time module.

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

    def __init__(self, history, contain_deleted=()):
        self._history = history
        self._docs = dict([(doc.docid, doc) for doc in history])
        self._reverted = []
        self.containers = []
        self.contain_deleted = set(contain_deleted)

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

    def filter_container_ids(self, container_ids):
        res = []
        for container_id in container_ids:
            contents = self._docs.get(container_id)
            if contents is not None and hasattr(contents, 'map'):
                res.append(container_id)
        return res

    def which_contain_deleted(self, container_ids):
        return list(self.contain_deleted.intersection(set(container_ids)))


class Dummy(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)


def DummyAdapter(obj):
    return obj


class DummyCatalog(object):

    def __init__(self):
        self.reindexed = []

    def reindex_doc(self, docid, doc):
        self.reindexed.append((docid, doc))
