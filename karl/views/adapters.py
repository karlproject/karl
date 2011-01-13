from repoze.bfg.chameleon_zpt import render_template
from repoze.bfg.url import model_url
from repoze.lemonade.listitem import get_listitems

from karl.content.interfaces import IBlogEntry
from karl.content.interfaces import IForum
from karl.models.interfaces import ICommunityInfo
from karl.models.interfaces import IIntranets
from karl.models.interfaces import ISite
from karl.models.interfaces import IToolFactory
from karl.utils import find_community
from karl.utils import find_interface
from karl.views.interfaces import IFooter
from karl.views.interfaces import ILiveSearchEntry
from karl.views.interfaces import IToolAddables
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import implements

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
        return render_template(
            'templates/footer.pt',
            api=api,
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
                       url=model_url(context, request))
    return dict(common_elts, **kwargs)

@implementer(ILiveSearchEntry)
def generic_livesearch_result(context, request):
    return livesearch_dict(context, request)

@implementer(ILiveSearchEntry)
def profile_livesearch_result(context, request):
    return livesearch_dict(
        context, request,
        extension=context.extension,
        email=context.email,
        type='profile',
        category='profile',
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
    # XXX can add in url to icon representing type of file

    return livesearch_dict(
        context, request,
        modified_by=context.modified_by,
        modified=context.modified.isoformat(),
        type='file',
        category='file',
        )

@implementer(ILiveSearchEntry)
def community_livesearch_result(context, request):
    community_info = getMultiAdapter((context, request), ICommunityInfo)
    return livesearch_dict(
        context, request,
        num_members=community_info.number_of_members,
        type='other',
        category='community',
        )

@implementer(ILiveSearchEntry)
def calendar_livesearch_result(context, request):
    return livesearch_dict(
        context, request,
        community=_community_title(context),
        start=context.startDate.isoformat(),
        end=context.endDate.isoformat(),
        location=context.location,
        type='other',
        category='calendarevent',
        )
