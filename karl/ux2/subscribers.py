from karl.utilities.interfaces import IContextTools


def add_renderer_globals(event):
    context, request = event['context'], event['request']
    context_tools_factory = request.registry.getUtility(IContextTools)
    event['context_tools'] = context_tools_factory(context, request)
