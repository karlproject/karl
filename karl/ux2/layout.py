from bottlecap.layouts.popper.layout import PopperLayout

from pyramid.decorator import reify
from pyramid.renderers import get_renderer
from pyramid.security import effective_principals
from pyramid.security import has_permission
from pyramid.traversal import find_resource
from pyramid.url import resource_url

from karl.security.policy import VIEW
from karl.utils import find_intranet
from karl.utils import find_site


class Layout(PopperLayout):
    page_title = 'Page Title'
    extra_css = ('karl.views:static/ux2/main.css',)

    def __init__(self, context, request):
        super(Layout, self).__init__(context, request)
        self.settings = settings = request.registry.settings

        self.app_url = app_url = request.application_url
        self.here_url = resource_url(context, request)
        self.current_intranet = find_intranet(context)
        self.people_url = app_url + '/' + settings.get('people_path', 'people')
        self.site = find_site(context)
        self.project_name = settings.get('system_name', 'KARL')

    @reify
    def should_show_calendar_tab(self):
        path = self.settings.get('global_calendar_path', '/offices/calendar')
        try:
            calendar = find_resource(self.context, path)
        except KeyError:
            return False

        return has_permission(VIEW, calendar, self.request)

    @reify
    def user_is_staff(self):
        return 'group.KarlStaff' in effective_principals(self.request)

    @reify
    def user_is_admin(self):
        return 'group.KarlAdmin' in effective_principals(self.request)

    @reify
    def macros(self):
        return get_renderer('templates/macros.pt').implementation().macros

    def static(self, fname):
        return self.request.static_url('karl.views:static/%s' % fname)
