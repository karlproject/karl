import unittest
from repoze.bfg import testing
from zope.testing.cleanup import cleanUp


class Test_show_history(unittest.TestCase):

    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

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
                user='ed',
                archive_time=datetime(2010, 5, 12, 2, 42),
                version_num=1,
                current_version=2,
            ),
            Dummy(
                user='ed',
                archive_time=datetime(2010, 5, 13, 2, 42),
                version_num=2,
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

    def test_it_no_repo(self):
        request = testing.DummyRequest()
        context = testing.DummyModel(
            docid=3,
            title='Title',
        )
        result = self._callFUT(context, request)
        history = result['history']
        self.assertEqual(len(history), 0)

class Test_revert(unittest.TestCase):

    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

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
            Dummy(version_num=1,),
            Dummy(version_num=2,),
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
            Dummy(version_num=1,),
            Dummy(version_num=2,),
        ])
        self.assertRaises(ValueError, self._callFUT, context, request)


class Test_show_trash(unittest.TestCase):

    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.versions import show_trash
        return show_trash(context, request, tz=5 * 3600)

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
                deleted_by='ed',
                deleted_time=datetime(2010, 5, 12, 2, 42),
                docid=2,
                name="foo2",
                title="Title 2",
            ),
            Dummy(
                deleted_by='ed',
                deleted_time=datetime(2010, 5, 13, 2, 42),
                docid=3,
                name="foo3",
                title="Title 3",
            ),
        ])
        result = self._callFUT(context, request)
        history = result['deleted']
        self.assertEqual(len(history), 2)
        self.assertEqual(len(history[0]), 4)
        self.assertEqual(history[0]['date'], '2010-05-11 21:42')
        self.assertEqual(history[0]['deleted_by'], {
            'name': 'Ed', 'url': 'http://example.com/profiles/ed/'})
        self.assertEqual(history[0]['restore_url'],
                         'http://example.com/restore?docid=2&name=foo2')
        self.assertEqual(history[0]['title'], 'Title 2')
        self.assertEqual(len(history[1]), 4)
        self.assertEqual(history[1]['date'], '2010-05-12 21:42')
        self.assertEqual(history[1]['deleted_by'], {
            'name': 'Ed', 'url': 'http://example.com/profiles/ed/'})
        self.assertEqual(history[1]['restore_url'],
                         'http://example.com/restore?docid=3&name=foo3')
        self.assertEqual(history[1]['title'], 'Title 3')

    def test_it_no_repo(self):
        request = testing.DummyRequest()
        context = testing.DummyModel(
            docid=3,
            title='Title',
        )
        result = self._callFUT(context, request)
        history = result['deleted']
        self.assertEqual(len(history), 0)


class Test_undelete(unittest.TestCase):

    def setUp(self):
        cleanUp()

        from zope.interface import Interface
        from karl.models.interfaces import IContainerVersion
        testing.registerAdapter(DummyAdapter, Interface, IContainerVersion)

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.versions import undelete
        return undelete(context, request)

    def _make_repo(self, context):
        from datetime import datetime
        context.repo = DummyArchive([
            Dummy(
                klass=DummyModel,
                deleted_by='ed',
                deleted_time=datetime(2010, 5, 12, 2, 42),
                docid=2,
                name="foo2",
                title="Title 2",
            ),
            Dummy(
                klass=DummyModel,
                deleted_by='ed',
                deleted_time=datetime(2010, 5, 13, 2, 42),
                docid=33,
                name="foo3",
                title="Title 3",
            ),
        ])
        context.repo.maps.append({'foo3': 33})

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
        self.assertEqual(result.location, 'http://example.com/foo2/')
        self.assertEqual(context['foo2'].reverted[0].docid, 2)
        self.assertEqual(len(context['foo2'].reverted), 1)
        self.assertEqual(context['foo2']['foo3'].reverted[0].docid, 33)
        self.assertEqual(len(context['foo2']['foo3'].reverted), 1)
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
        self.assertEqual(result.location, 'http://example.com/foo2-1/')
        self.assertEqual(context['foo2-1'].reverted[0].docid, 2)
        self.assertEqual(len(context['foo2-1'].reverted), 1)
        self.assertEqual(context['foo2-1']['foo3'].reverted[0].docid, 33)
        self.assertEqual(len(context['foo2-1']['foo3'].reverted), 1)
        self.assertEqual(context.repo.containers, [(context, None)])


class Test_show_history_lock(unittest.TestCase):

    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.views.versions import show_history
        return show_history(context, request)

    def test_show_locked_page(self):
        from karl.testing import DummyRoot
        site = DummyRoot()
        context = testing.DummyModel(title='title')
        site['foo'] = context

        import datetime
        lock_time = datetime.datetime.now() - datetime.timedelta(seconds=1)
        context.lock = {'time': lock_time,
                        'userid': 'foo'}

        request = testing.DummyRequest()
        response = self._callFUT(context, request)
        self.failUnless(response['lock_info']['is_locked'])


class DummyArchive(object):

    def __init__(self, history):
        self._history = history
        self._reverted = []
        self.maps = []
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
        if docid == 33:
            raise KeyError(docid)
        return self

    @property
    def deleted(self):
        return self._history

    @property
    def map(self):
        if self.maps:
            return self.maps.pop(0)
        return {}

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
