from karl.models.interfaces import ICommunityInfo
from karl.utilities.interfaces import IContextTools
from karl.utils import find_community
from zope.component import getMultiAdapter
from zope.interface import implementer


@implementer(IContextTools)
def context_tools(context, request):
    community = find_community(context)
    if community is None:
        return None
    community_info = getMultiAdapter((community, request), ICommunityInfo)
    if community_info is not None:
        return community_info.tabs
