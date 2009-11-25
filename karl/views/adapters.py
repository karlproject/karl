from karl.content.interfaces import ICalendarEvent
from karl.content.interfaces import IForum
from karl.content.interfaces import IReferencesFolder
from karl.content.interfaces import IReferenceManual
from karl.content.interfaces import IReferenceSection
from karl.content.views.interfaces import INetworkEventsMarker
from karl.content.views.interfaces import INetworkNewsMarker
from karl.models.interfaces import IIntranet
from karl.models.interfaces import IIntranets
from karl.models.interfaces import IToolFactory
from karl.views import site
from karl.views.interfaces import ILayoutProvider
from karl.views.interfaces import IToolAddables
from os.path import join
from repoze.bfg.chameleon_zpt import get_template
from repoze.bfg.path import package_path
from repoze.bfg.traversal import find_interface
from repoze.lemonade.listitem import get_listitems
from zope.interface import implements

EXCLUDE_TOOLS = ['intranets',]

class DefaultToolAddables(object):
    implements(IToolAddables)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        """ What tools can go in a community?
        """
        tools = get_listitems(IToolFactory)
        return [tool for tool in tools if tool['name'] not in EXCLUDE_TOOLS]

class DefaultFolderAddables(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        """ Based on markers, override what can be added to a folder """

        # This is the default for all, meaning community, folders
        _addlist = [
            ('Add Folder', 'add_folder.html'),
            ('Add File', 'add_file.html'),
            ]

        # Intranet folders by default get Add Page
        intranets = find_interface(self.context, IIntranets)
        if intranets:
            _addlist.append(
                ('Add Event', 'add_calendarevent.html'),
                )
            _addlist.append(
                ('Add Page', 'add_page.html'),
                )

        # Override all addables in certain markers
        if IReferencesFolder.providedBy(self.context):
            _addlist = [('Add Reference Manual',
                         'add_referencemanual.html')]
        elif IReferenceManual.providedBy(self.context):
            _addlist = [
                ('Add Section', 'add_referencesection.html'),
                ]
        elif IReferenceSection.providedBy(self.context):
            _addlist = [
                ('Add File', 'add_file.html'),
                ('Add Page', 'add_page.html'),
                ]
        elif INetworkEventsMarker.providedBy(self.context):
            _addlist = [
                ('Add Event', 'add_calendarevent.html'),
                ]
        elif INetworkNewsMarker.providedBy(self.context):
            _addlist = [
                ('Add News Item', 'add_newsitem.html'),
                ]
        return _addlist


class DefaultLayoutProvider(object):
    """ Site policy on which o-wrap to choose from for a context"""
    implements(ILayoutProvider)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def community_layout(self):
        package_dir = package_path(site)
        template_fn = join(package_dir, 'templates', 'community_layout.pt')
        return get_template(template_fn)

    @property
    def generic_layout(self):
        package_dir = package_path(site)
        template_fn = join(package_dir, 'templates', 'generic_layout.pt')
        return get_template(template_fn)

    @property
    def intranet_layout(self):
        layout = get_template('templates/intranet_layout.pt')
        intranet = find_interface(self.context, IIntranet)
        if intranet:
            layout.navigation = intranet.navigation
        return layout

    def __call__(self, default=None):
        # The layouts are by identifier, e.g. layout='community'

        # A series of tests, in order of precedence.
        layout = None
        if default is not None:
            layout = getattr(self, default+'_layout')
        intranet = find_interface(self.context, IIntranet)

        # Group a series of intranet-oriented decisions
        if intranet:
            # First, when under an intranet, OSI wants forums to get
            # the generic layout.
            if find_interface(self.context, IForum):
                layout = getattr(self, 'generic_layout')

            # Now for an intranet.  Everything gets the two-column
            # view except the intranet home page, which gets the 3
            # column treatment.
            else:
                layout = getattr(self, 'intranet_layout')

        elif find_interface(self.context, IIntranets):
            if find_interface(self.context, IForum):
                layout = getattr(self, 'generic_layout')
            elif ICalendarEvent.providedBy(self.context):
                layout = getattr(self, 'generic_layout')
            elif INetworkNewsMarker.providedBy(self.context):
                layout = getattr(self, 'generic_layout')
            elif find_interface(self.context, IReferencesFolder):
                layout = getattr(self, 'generic_layout')
            elif INetworkEventsMarker.providedBy(self.context):
                layout = getattr(self, 'generic_layout')

        return layout

