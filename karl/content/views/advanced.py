import formish
import schemaish

from repoze.bfg.traversal import find_interface
from repoze.bfg.url import model_url
from webob.exc import HTTPFound
from zope.component import queryAdapter
from zope.component.event import objectEventNotify
from zope.interface import alsoProvides
from zope.interface import noLongerProvides

from karl.content.interfaces import ICommunityFolder
from karl.content.interfaces import IReferencesFolder
from karl.content.views.interfaces import INetworkNewsMarker
from karl.content.views.interfaces import INetworkEventsMarker
from karl.events import ObjectModifiedEvent
from karl.events import ObjectWillBeModifiedEvent
from karl.models.interfaces import IIntranets
from karl.utilities import lock
from karl.utils import get_layout_provider
from karl.views.api import TemplateAPI
from karl.views.forms import widgets


marker_field = schemaish.String(
    title='Marker',
    description='Customize what flavor of folder this is by choosing one of '
    'the following markers.')

keywords_field = schemaish.Sequence(
    schemaish.String(),
    title='Search Keywords',
    description='This document will be shown first for searches for any of '
    'these keywords')

weight_field = schemaish.Integer(
    title='Search Weight',
    description='Modify the relative importance of this document in search '
    'results.')

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

keywords_widget = widgets.SequenceTextAreaWidget(cols=20)

weight_options = [
    (-1, 'Less important'), # I bet no one ever uses this one.
    (0, 'Normal'),
    (1, 'More important'),
    (2, 'Much more important'),
]

weight_widget = formish.SelectChoice(
    options=weight_options,
    none_option=None,
)

unlock_field = schemaish.Boolean(
    title='Force unlock',
    description='This wiki page is currently locked. Force unlock it.',
)

class UnlockWidget(widgets.Checkbox):
    checkbox_label = 'Unlock'
unlock_widget = UnlockWidget()

class AdvancedFormController(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

        in_intranets = find_interface(context, IIntranets) is not None
        is_folder = ICommunityFolder.providedBy(context)
        self.use_folder_options = is_folder and in_intranets

        self.use_unlock = lock.is_locked(context)

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

        defaults['keywords'] = getattr(context, 'search_keywords', [])
        defaults['weight'] = getattr(context, 'search_weight', 0)

        if self.use_unlock:
            defaults['unlock'] = False

        return defaults

    def form_fields(self):
        fields = []
        if self.use_folder_options:
            fields.append(('marker', marker_field))
        fields.append(('keywords', keywords_field))
        fields.append(('weight', weight_field))

        if self.use_unlock:
            fields.append(('unlock', unlock_field))

        return fields

    def form_widgets(self, fields):
        form_widgets = {}
        if self.use_folder_options:
            form_widgets['marker'] = marker_widget
        form_widgets['keywords'] = keywords_widget
        form_widgets['weight'] = weight_widget
        if self.use_unlock:
            form_widgets['unlock'] = unlock_widget
        return form_widgets

    def __call__(self):
        api = TemplateAPI(self.context, self.request, self.page_title)
        layout_provider = get_layout_provider(self.context, self.request)
        layout = layout_provider('community')
        return {'api':api, 'actions':(), 'layout':layout}

    def handle_cancel(self):
        return HTTPFound(location=model_url(self.context, self.request))

    def handle_submit(self, params):
        context = self.context
        objectEventNotify(ObjectWillBeModifiedEvent(context))

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

        keywords = params.get('keywords')
        if keywords is not None:
            context.search_keywords = keywords

        weight = params.get('weight')
        if weight is not None:
            context.search_weight = weight

        if self.use_unlock and params.get('unlock'):
            lock.clear(context)

        objectEventNotify(ObjectModifiedEvent(context))
        return HTTPFound(location=model_url(self.context, self.request,
                    query={'status_message': 'Advanced settings changed.'}))
