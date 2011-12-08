from pyramid.decorator import reify
from pyramid.renderers import get_renderer

from bottlecap.layout import LayoutManager as BaseLayoutManager

class LayoutManager(BaseLayoutManager):

    @property
    def global_nav_menus(self):
        menu_items = [
            dict(title="Intranet", selected=None),
            dict(title="Communities", selected="selected"),
            dict(title="People", selected=None),
            dict(title="Calendar", selected=None),
            dict(title="Explore", selected=None),
            ]
        return menu_items

    @reify
    def snippets(self):
        template = get_renderer('karl:views/templates/snippets.pt')
        return template.implementation()


def global_nav(context, request):
    return {}
