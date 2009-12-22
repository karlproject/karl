from repoze.bfg.chameleon_zpt import render_template
from repoze.lemonade.listitem import get_listitems

from karl.models.interfaces import IIntranets
from karl.models.interfaces import ISite
from karl.models.interfaces import IToolFactory
from karl.utils import find_interface
from karl.views.interfaces import IFooter
from karl.views.interfaces import IToolAddables
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
