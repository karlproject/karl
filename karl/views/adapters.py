import logging

from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import implements

from pyramid.renderers import render
from pyramid.url import resource_url
from repoze.lemonade.listitem import get_listitems

from karl.content.interfaces import IBlogEntry
from karl.content.interfaces import IForum
from karl.content.views.interfaces import IFileInfo
from karl.models.interfaces import ICommunityInfo
from karl.models.interfaces import IIntranets
from karl.models.interfaces import ISite
from karl.models.interfaces import IToolFactory
from karl.utilities.image import thumb_url
from karl.utilities.interfaces import IKarlDates
from karl.utils import find_community
from karl.utils import find_interface
from karl.views.interfaces import IAdvancedSearchResultsDisplay
from karl.views.interfaces import IFooter
from karl.views.interfaces import ILiveSearchEntry
from karl.views.interfaces import IToolAddables
from karl.views.utils import get_static_url


log = logging.getLogger(__name__)


class DefaultToolAddables(object):
    implements(IToolAddables)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        """ What tools can go in a community?
        """
        tools = get_listitems(IToolFactory)
        return [tool for tool in tools if tool['name'] not in
                self.exclude_tools]

    @property
    def exclude_tools(self):
        # Find out if we are adding this community from somewhere
        # inside the "intranets" side
        intranets = find_interface(self.context, IIntranets)
        site = ISite.providedBy(self.context)

        if intranets or site:
            return ['wiki', 'blog']

        return ['intranets', 'forums']


class DefaultFooter(object):
    implements(IFooter)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, api):
        return render(
            'templates/footer.pt',
            dict(api=api),
            request=self.request,
            )

def _parent_title(context, class_or_interface):
    """helper to find the title of an object in the parent graph"""
    obj = find_interface(context, class_or_interface)
    return obj and obj.title

def _community_title(context):
    """find the title of a community

    offices also provide ICommunity, but we don't want to consider those
    here. offices explicitly provide IIntranets, so we'll discount those that
    way
    """
    obj = find_community(context)
    if obj is None or IIntranets.providedBy(obj):
        return None
    return obj.title

def livesearch_dict(context, request, **kwargs):
    """helper to add some common elements to the livesearch result"""
    common_elts = dict(title=getattr(context, 'title', '<No Title>'),
                       url=resource_url(context, request))
    return dict(common_elts, **kwargs)

@implementer(ILiveSearchEntry)
def generic_livesearch_result(context, request):
    return livesearch_dict(context, request)

@implementer(ILiveSearchEntry)
def profile_livesearch_result(context, request):
    photo = context.get('photo')
    if photo is None:
        thumbnail = get_static_url(request) + '/images/defaultUser.gif'
    else:
        thumbnail = thumb_url(photo, request, (85,85))
    return livesearch_dict(
        context, request,
        extension=context.extension,
        email=context.email,
        department=context.department,
        type='profile',
        category='profile',
        thumbnail=thumbnail,
        )

@implementer(ILiveSearchEntry)
def page_livesearch_result(context, request):
    return livesearch_dict(
        context, request,
        modified_by=context.modified_by,
        modified=context.modified.isoformat(),
        community=_community_title(context),
        type='page',
        category='page',
        )

@implementer(ILiveSearchEntry)
def reference_livesearch_result(context, request):
    return livesearch_dict(
        context, request,
        modified_by=context.modified_by,
        modified=context.modified.isoformat(),
        type='page',
        category='reference',
        )

@implementer(ILiveSearchEntry)
def blogentry_livesearch_result(context, request):
    return livesearch_dict(
        context, request,
        modified_by=context.modified_by,
        modified=context.modified.isoformat(),
        community=_community_title(context),
        type='post',
        category='blogentry',
        )

@implementer(ILiveSearchEntry)
def comment_livesearch_result(context, request):
    return livesearch_dict(
        context, request,
        creator=context.creator,
        created=context.created.isoformat(),
        community=_community_title(context),
        forum=_parent_title(context, IForum),
        blog=_parent_title(context, IBlogEntry),
        type='post',
        category='comment',
        )

@implementer(ILiveSearchEntry)
def forum_livesearch_result(context, request):
    return livesearch_dict(
        context, request,
        creator=context.creator,
        created=context.created.isoformat(),
        type='post',
        category='forum',
        )

@implementer(ILiveSearchEntry)
def forumtopic_livesearch_result(context, request):
    return livesearch_dict(
        context, request,
        creator=context.creator,
        created=context.created.isoformat(),
        forum=_parent_title(context, IForum),
        type='post',
        category='forumtopic',
        )

@implementer(ILiveSearchEntry)
def file_livesearch_result(context, request):
    fileinfo = getMultiAdapter((context, request), IFileInfo)
    static_url = get_static_url(request)
    icon =  "%s/images/%s" % (static_url, fileinfo.mimeinfo['small_icon_name'])
    return livesearch_dict(
        context, request,
        modified_by=context.modified_by,
        modified=context.modified.isoformat(),
        icon=icon,
        community=_community_title(context),
        type='file',
        category='file',
        )

@implementer(ILiveSearchEntry)
def community_livesearch_result(context, request):
    community_info = getMultiAdapter((context, request), ICommunityInfo)
    return livesearch_dict(
        context, request,
        num_members=community_info.number_of_members,
        type='community',
        category='community',
        )

@implementer(ILiveSearchEntry)
def intranet_livesearch_result(context, request):
    return livesearch_dict(
        context, request,
        address=context.address,
        city=context.city,
        state=context.state,
        zipcode=context.zipcode,
        telephone=context.telephone,
        country=context.country,
        type='community',
        category='office',
        )

@implementer(ILiveSearchEntry)
def calendar_livesearch_result(context, request):
    return livesearch_dict(
        context, request,
        community=_community_title(context),
        start=context.startDate.isoformat(),
        end=context.endDate.isoformat(),
        location=context.location,
        type='calendarevent',
        category='calendarevent',
        )

class BaseAdvancedSearchResultsDisplay(object):
    implements(IAdvancedSearchResultsDisplay)

    panel = macro = 'searchresults_generic'
    display_data = {}

    def __init__(self, context, request):
        self.context = context
        self.request = request

class AdvancedSearchResultsDisplayOffice(BaseAdvancedSearchResultsDisplay):
    panel = macro = 'searchresults_office'

class AdvancedSearchResultsDisplayPeople(BaseAdvancedSearchResultsDisplay):
    panel = macro = 'searchresults_people'

    def __init__(self, context, request):
        super(AdvancedSearchResultsDisplayPeople, self).__init__(context,
                                                                 request)
        contact_items = []
        if context.extension and context.extension.strip():
            extension_html = ('<span class="sras-people-extension">x%s</span>'
                              % context.extension)
            contact_items.append(extension_html)
        if context.room_no and context.room_no.strip():
            room_html = ('<span class="sras-people-room">Room %s</span>'
                         % context.room_no)
            contact_items.append(room_html)
        if context.email and context.email.strip():
            email_html = ('<a href="mailto:%s">%s</a>'
                          % (context.email, context.email))
            contact_items.append(email_html)

        photo = context.get('photo')
        if photo is None:
            thumbnail = get_static_url(request) + '/images/defaultUser.gif'
        else:
            thumbnail = thumb_url(photo, request, (50,50))

        self.display_data = dict(
            contact_html = ' - '.join(contact_items),
            thumbnail = thumbnail,
            )

class AdvancedSearchResultsDisplayEvent(BaseAdvancedSearchResultsDisplay):
    panel = macro = 'searchresults_event'

    def __init__(self, context, request):
        super(AdvancedSearchResultsDisplayEvent, self).__init__(context,
                                                                request)

        karldates = getUtility(IKarlDates)
        startDate = karldates(context.startDate, 'longform')
        endDate = karldates(context.endDate, 'longform')
        location = context.location

        self.display_data = dict(
            startDate = startDate,
            endDate = endDate,
            location = location,
            )

class AdvancedSearchResultsDisplayFile(BaseAdvancedSearchResultsDisplay):
    panel = macro = 'searchresults_file'

    def __init__(self, context, request):
        super(AdvancedSearchResultsDisplayFile, self).__init__(context,
                                                               request)

        fileinfo = getMultiAdapter((context, request), IFileInfo)
        icon = (get_static_url(request) + "/images/" +
                fileinfo.mimeinfo['small_icon_name'])

        self.display_data = dict(
            fileinfo = fileinfo,
            icon = icon,
            )
