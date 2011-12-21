from pyramid.decorator import reify

from karl.utils import find_intranets
from karl.views.api import TemplateAPI


class Layout(TemplateAPI):

    def __init__(self, context, request):
        super(Layout, self).__init__(context, request)
        self.popper_static_url = request.static_url(
            'bottlecap.layouts.popper:static/')

    @reify
    def global_nav_menus(self):
        request = self.request
        site = self.site
        menu_items = [
            dict(title="Communities",
                 url=request.resource_url(site, 'communities'),
                 selected='selected'),
            dict(title="People",
                 url=self.people_url,
                 selected=None),
            dict(title="Feeds",
                 url=request.resource_url(site, 'contentfeeds.html'),
                 selected=None),
            ]
        intranets = find_intranets(site)
        if self.current_intranet is not None:
            menu_items.insert(0, dict(title="Intranet",
                 url=request.resource_url(intranets),
                 selected=None))
        if self.should_show_calendar_tab:
            menu_items.append(dict(title="Calendar",
                 url=request.resource_url(site, 'offices', 'calendar'),
                 selected=None))
        if self.user_is_staff:
            menu_items.append(dict(title="Tags",
                 url=request.resource_url(site, 'tagcloud.html'),
                 selected=None))
        return menu_items
