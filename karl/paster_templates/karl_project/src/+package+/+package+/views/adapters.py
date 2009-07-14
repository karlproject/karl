from zope.interface import implements
from repoze.lemonade.listitem import get_listitems
from karl.models.interfaces import IToolFactory
from karl.views.interfaces import IToolAddables

class ToolAddables(object):
    implements(IToolAddables)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        """ What tools can go in a community?
        """
        return get_listitems(IToolFactory)
