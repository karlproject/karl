import unittest

from repoze.bfg import testing
from karl import testing as karltesting
from zope.testing.cleanup import cleanUp

class TestAdvancedFormController(unittest.TestCase):

    def setUp(self):
        cleanUp()
        karltesting.registerLayoutProvider()

    def tearDown(self):
        cleanUp()

    def _make_one(self, context, request):
        from karl.content.views.advanced import AdvancedFormController as cut
        return cut(context, request)

    def test_form_defaults(self):
        context = testing.DummyModel()
        request = testing.DummyRequest()
        form = self._make_one(context, request)
        self.assertEqual(form.form_defaults(), {})

    def test_form_defaults_is_intranet_folder(self):
        from karl.models.interfaces import IIntranets
        from karl.content.interfaces import ICommunityFolder
        context = testing.DummyModel(
            __provides__=(IIntranets, ICommunityFolder))
        request = testing.DummyRequest()
        form = self._make_one(context, request)
        self.assertEqual(form.form_defaults(), {'marker': ''})

    def test_form_defaults_is_references_folder(self):
        from karl.models.interfaces import IIntranets
        from karl.content.interfaces import ICommunityFolder
        from karl.content.interfaces import IReferencesFolder
        context = testing.DummyModel(
            __provides__=(IIntranets, ICommunityFolder, IReferencesFolder))
        request = testing.DummyRequest()
        form = self._make_one(context, request)
        self.assertEqual(form.form_defaults(), {'marker': 'reference_manual'})

    def test_form_defaults_is_network_news(self):
        from karl.models.interfaces import IIntranets
        from karl.content.interfaces import ICommunityFolder
        from karl.content.views.interfaces import INetworkNewsMarker
        context = testing.DummyModel(
            __provides__=(IIntranets, ICommunityFolder, INetworkNewsMarker))
        request = testing.DummyRequest()
        form = self._make_one(context, request)
        self.assertEqual(form.form_defaults(), {'marker': 'network_news'})

    def test_form_defaults_is_network_events(self):
        from karl.models.interfaces import IIntranets
        from karl.content.interfaces import ICommunityFolder
        from karl.content.views.interfaces import INetworkEventsMarker
        context = testing.DummyModel(
            __provides__=(IIntranets, ICommunityFolder, INetworkEventsMarker))
        request = testing.DummyRequest()
        form = self._make_one(context, request)
        self.assertEqual(form.form_defaults(), {'marker': 'network_events'})

    def test_form_fields(self):
        context = testing.DummyModel()
        request = testing.DummyRequest()
        form = self._make_one(context, request)
        self.assertEqual(form.form_fields(), [])

    def test_form_fields_is_intranet_folder(self):
        from karl.models.interfaces import IIntranets
        from karl.content.interfaces import ICommunityFolder
        from karl.content.views.advanced import marker_field
        context = testing.DummyModel(
            __provides__=(IIntranets, ICommunityFolder))
        request = testing.DummyRequest()
        form = self._make_one(context, request)
        self.assertEqual(form.form_fields(), [('marker', marker_field)])

    def test_form_widgets(self):
        context = testing.DummyModel()
        request = testing.DummyRequest()
        form = self._make_one(context, request)
        self.assertEqual(form.form_widgets(None), {})

    def test_form_widgets_is_intranet_folder(self):
        from karl.models.interfaces import IIntranets
        from karl.content.interfaces import ICommunityFolder
        from karl.content.views.advanced import marker_widget
        context = testing.DummyModel(
            __provides__=(IIntranets, ICommunityFolder))
        request = testing.DummyRequest()
        form = self._make_one(context, request)
        self.assertEqual(form.form_widgets(None), {'marker': marker_widget})

    def test___call__(self):
        context = testing.DummyModel()
        request = testing.DummyRequest()
        form = self._make_one(context, request)
        response = form()
        self.failUnless('api' in response)
        self.failUnless('actions' in response)
        self.failUnless('layout' in response)
        self.failUnless(response['api'].page_title)

    def test_handle_cancel(self):
        context = testing.DummyModel()
        request = testing.DummyRequest()
        form = self._make_one(context, request)
        response = form.handle_cancel()
        self.assertEqual(response.status_int, 302)
        self.assertEqual(response.location, 'http://example.com/')

    def test_handle_submit(self):
        context = testing.DummyModel()
        request = testing.DummyRequest()
        form = self._make_one(context, request)
        response = form.handle_submit({})
        self.assertEqual(response.status_int, 302)
        self.assertEqual(response.location,
            'http://example.com/?status_message=Advanced+settings+changed.')

    def test_handle_submit_no_marker(self):
        from karl.models.interfaces import IIntranets
        from karl.content.interfaces import ICommunityFolder
        from karl.content.interfaces import IReferencesFolder
        from karl.content.views.interfaces import INetworkEventsMarker
        from karl.content.views.interfaces import INetworkNewsMarker
        context = testing.DummyModel(
            __provides__=(IIntranets, ICommunityFolder))
        request = testing.DummyRequest()
        form = self._make_one(context, request)
        response = form.handle_submit({})
        self.failIf(IReferencesFolder.providedBy(context))
        self.failIf(INetworkEventsMarker.providedBy(context))
        self.failIf(INetworkNewsMarker.providedBy(context))
        self.assertEqual(response.status_int, 302)
        self.assertEqual(response.location,
            'http://example.com/?status_message=Advanced+settings+changed.')

    def test_handle_submit_set_reference_manual_marker(self):
        from karl.models.interfaces import IIntranets
        from karl.content.interfaces import ICommunityFolder
        from karl.content.interfaces import IReferencesFolder
        from karl.content.views.interfaces import INetworkEventsMarker
        from karl.content.views.interfaces import INetworkNewsMarker
        context = testing.DummyModel(
            __provides__=(IIntranets, ICommunityFolder))
        request = testing.DummyRequest()
        form = self._make_one(context, request)
        response = form.handle_submit({'marker': 'reference_manual'})
        self.failUnless(IReferencesFolder.providedBy(context))
        self.failIf(INetworkEventsMarker.providedBy(context))
        self.failIf(INetworkNewsMarker.providedBy(context))
        self.assertEqual(response.status_int, 302)
        self.assertEqual(response.location,
            'http://example.com/?status_message=Advanced+settings+changed.')

    def test_handle_submit_set_network_events_marker(self):
        from karl.models.interfaces import IIntranets
        from karl.content.interfaces import ICommunityFolder
        from karl.content.interfaces import IReferencesFolder
        from karl.content.views.interfaces import INetworkEventsMarker
        from karl.content.views.interfaces import INetworkNewsMarker
        context = testing.DummyModel(
            __provides__=(IIntranets, ICommunityFolder))
        request = testing.DummyRequest()
        form = self._make_one(context, request)
        response = form.handle_submit({'marker': 'network_events'})
        self.failIf(IReferencesFolder.providedBy(context))
        self.failUnless(INetworkEventsMarker.providedBy(context))
        self.failIf(INetworkNewsMarker.providedBy(context))
        self.assertEqual(response.status_int, 302)
        self.assertEqual(response.location,
            'http://example.com/?status_message=Advanced+settings+changed.')

    def test_handle_submit_set_network_news_marker(self):
        from karl.models.interfaces import IIntranets
        from karl.content.interfaces import ICommunityFolder
        from karl.content.interfaces import IReferencesFolder
        from karl.content.views.interfaces import INetworkEventsMarker
        from karl.content.views.interfaces import INetworkNewsMarker
        context = testing.DummyModel(
            __provides__=(IIntranets, ICommunityFolder))
        request = testing.DummyRequest()
        form = self._make_one(context, request)
        response = form.handle_submit({'marker': 'network_news'})
        self.failIf(IReferencesFolder.providedBy(context))
        self.failIf(INetworkEventsMarker.providedBy(context))
        self.failUnless(INetworkNewsMarker.providedBy(context))
        self.assertEqual(response.status_int, 302)
        self.assertEqual(response.location,
            'http://example.com/?status_message=Advanced+settings+changed.')

