from repoze.bfg.chameleon_zpt import render_template
from repoze.lemonade.listitem import get_listitems

from karl.models.interfaces import IToolFactory
from karl.views.interfaces import IFooter
from karl.views.interfaces import IToolAddables
from zope.interface import implements

class DefaultToolAddables(object):
    implements(IToolAddables)

    exclude_tools = ['intranets',]

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        """ What tools can go in a community?
        """
        tools = get_listitems(IToolFactory)
        return [tool for tool in tools if tool['name'] not in
                self.exclude_tools]


class SiteToolAddables(DefaultToolAddables):
    """ For tools in community at site root.
    """
    exclude_tools = ['wiki', 'blog',]

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
