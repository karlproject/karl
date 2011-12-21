from pyramid.decorator import reify
from pyramid.renderers import get_renderer

from bottlecap.layouts.popper.layout import PopperLayout

from karl.views.api import TemplateAPI


class Layout(PopperLayout):

    @property
    def global_nav_menus(self):
        api = TemplateAPI(self.context, self.request)
        menu_items = [
            dict(title="Communities",
                 url="%s/communities" % api.app_url,
                 selected='selected'),
            dict(title="People",
                 url=api.people_url,
                 selected=None),
            dict(title="Feeds",
                 url="%s/contentfeeds.html" % api.app_url,
                 selected=None),
            ]
        if api.current_intranet is not None:
            menu_items.insert(0, dict(title="Intranet",
                 url="%s/offices" % api.app_url,
                 selected=None))
        if api.should_show_calendar_tab:
            menu_items.append(dict(title="Calendar",
                 url="%s/offices/calendar" % api.app_url,
                 selected=None))
        if api.user_is_staff:
            menu_items.append(dict(title="Tags",
                 url="%s/tagcloud.html" % api.app_url,
                 selected=None))
        return menu_items

    @reify
    def snippets(self):
        template = get_renderer('karl:views/templates/snippets.pt')
        return template.implementation()

