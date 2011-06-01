import formish
import schemaish

from repoze.bfg.traversal import find_interface
from repoze.bfg.url import model_url
from webob.exc import HTTPFound
from zope.interface import alsoProvides
from zope.interface import noLongerProvides

from karl.content.interfaces import ICommunityFolder
from karl.content.interfaces import IReferencesFolder
from karl.content.views.interfaces import INetworkNewsMarker
from karl.content.views.interfaces import INetworkEventsMarker
from karl.models.interfaces import IIntranets
from karl.utils import get_layout_provider
from karl.views.api import TemplateAPI
from karl.views.forms import widgets


marker_field = schemaish.String(
    title='Marker',
    description='Customize what flavor of folder this is by choosing one of '
    'the following markers.')

marker_options = [
    ('', 'No Marker'),
    ('reference_manual', 'Reference Manual'),
    ('network_events', 'Network Events'),
    ('network_news', 'Network News'),
]

marker_widget = widgets.VerticalRadioChoice(
    options=marker_options,
    none_option=None,
)


class AdvancedFormController(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

        in_intranets = find_interface(context, IIntranets) is not None
        is_folder = ICommunityFolder.providedBy(context)
        self.use_folder_options = is_folder and in_intranets

        title = getattr(context, 'title', context.__name__)
        self.page_title = 'Advanced Settings for %s' % title

    def form_defaults(self):
        defaults = {}
        context = self.context
        if self.use_folder_options:
            if IReferencesFolder.providedBy(context):
                defaults['marker'] = 'reference_manual'
            elif INetworkEventsMarker.providedBy(context):
                defaults['marker'] = 'network_events'
            elif INetworkNewsMarker.providedBy(context):
                defaults['marker'] = 'network_news'
            else:
                defaults['marker'] = ''

        return defaults

    def form_fields(self):
        fields = []
        if self.use_folder_options:
            fields.append(('marker', marker_field))
        return fields

    def form_widgets(self, fields):
        widgets = {}
        if self.use_folder_options:
            widgets['marker'] = marker_widget
        return widgets

    def __call__(self):
        api = TemplateAPI(self.context, self.request, self.page_title)
        layout_provider = get_layout_provider(self.context, self.request)
        layout = layout_provider('community')
        return {'api':api, 'actions':(), 'layout':layout}

    def handle_cancel(self):
        return HTTPFound(location=model_url(self.context, self.request))

    def handle_submit(self, params):
        context = self.context
        if self.use_folder_options:
            noLongerProvides(context, IReferencesFolder)
            noLongerProvides(context, INetworkNewsMarker)
            noLongerProvides(context, INetworkEventsMarker)
            marker = params.get('marker')
            if marker == 'reference_manual':
                alsoProvides(context, IReferencesFolder)
            elif marker == 'network_news':
                alsoProvides(context, INetworkNewsMarker)
            elif marker == 'network_events':
                alsoProvides(context, INetworkEventsMarker)

        return HTTPFound(location=model_url(self.context, self.request,
                    query={'status_message': 'Advanced settings changed.'}))
