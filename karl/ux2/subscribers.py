from karl.utilities.interfaces import IContextTools


def add_renderer_globals(event):
    context, request = event['context'], event['request']

    # In some cases this might be called because a template is rendering in the
    # context of a console script rather than a web application.  (Example,
    # rendering an email bounce message during mailin processing.)  In this case
    # request will be None.  While it is still possible to get the registry from
    # a thread local in this case, there is currently no need since we know we
    # don't need these renderer globals added in a console script context, so
    # we just skip it entirely.
    if request:
        context_tools_factory = request.registry.getUtility(IContextTools)
        event['context_tools'] = context_tools_factory(context, request)
