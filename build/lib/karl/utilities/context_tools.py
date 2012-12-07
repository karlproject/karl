from karl.models.interfaces import ICommunityInfo
from karl.utilities.interfaces import IContextTools
from karl.utils import find_community

from pyramid.traversal import resource_path

from zope.component import getMultiAdapter
from zope.interface import implementer


@implementer(IContextTools)
def context_tools(context, request):
    community = find_community(context)
    if community is None:
        return None
    community_info = getMultiAdapter((community, request), ICommunityInfo)

    tools = community_info.tabs
    members = community['members']
    members_path = resource_path(community['members'])
    context_path = resource_path(context)
    in_members = context_path.startswith(members_path)
    tools.append({
        'url': request.resource_url(members),
        'selected': in_members,
        'title': 'Members',
        'name':'members'})

    return tools
