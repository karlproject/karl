
import json

from pyramid.traversal import resource_path

from karl.utils import find_community


class JsonDict(dict):
    def __str__(self):
        return json.dumps(self)


class JsonList(list):
    def __str__(self):
        return json.dumps(self)


def searchbox_scope_options(context, request):
    scope_options = []
    scope_options.append(dict(
        path = '',
        name = 'all KARL',
        label = 'all KARL',
        selected = True,
        ))
    # We add a second option, in case, context is inside a community.
    community = find_community(context)
    if community:
        # We are in a community!
        scope_options.append(dict(
            path = resource_path(community),
            name = 'this community',
            label = community.title,
        ))
    return scope_options
