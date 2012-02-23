from bottlecap.layouts.popper.layout import PopperLayout

from pyramid.decorator import reify
from pyramid.renderers import get_renderer
from pyramid.security import effective_principals
from pyramid.security import has_permission
from pyramid.traversal import find_resource
from pyramid.url import resource_url

from karl.security.policy import VIEW
from karl.utils import find_community
from karl.utils import find_intranet
from karl.utils import find_site


class Layout(PopperLayout):

    def __init__(self, context, request):
        super(Layout, self).__init__(context, request)
        self.settings = settings = request.registry.settings

        self.app_url = app_url = request.application_url
        self.here_url = resource_url(context, request)
        self.current_intranet = find_intranet(context)
        self.people_url = app_url + '/' + settings.get('people_path', 'people')
        self.site = find_site(context)
        self.project_name = settings.get('system_name', 'KARL')
        self.page_title = getattr(context, 'title', 'Page Title')

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

    @apply
    def section_title():
        def getter(self):
            community = find_community(self.context)
            if community:
                title = community.title
            else:
                title = 'Section Title'  # annoying default to spur override
            self.__dict__['title'] = title  # reify
            return title

        def setter(self, title):
            self.__dict__['title'] = title  # reify

        return property(getter, setter)

    extra_css = (
        'karl.views:static/tinymce/tinymce-3.3.9.2.karl.css',
        'karl.views:static/ux2/main.css',)

    extra_js = (
        'karl.views:static/ux2/tinymce/karl-tiny-wire.js',
        'karl.views:static/tinymce/3.3.9.2/jquery.tinysafe.js',
        'karl.views:static/tinymce/3.3.9.2/tiny_mce_src.js',
        'karl.views:static/tinymce/3.3.9.2/langs/en.js',
        'karl.views:static/tinymce/3.3.9.2/themes/advanced/editor_template_src.js',
        'karl.views:static/tinymce/3.3.9.2/themes/advanced/langs/en.js',
        'karl.views:static/tinymce/3.3.9.2/plugins/paste/editor_plugin_src.js',
        'karl.views:static/tinymce/3.3.9.2/plugins/wicked/editor_plugin_src.js',
        'karl.views:static/tinymce/3.3.9.2/plugins/wicked/langs/en.js',
        'karl.views:static/tinymce/3.3.9.2/plugins/spellchecker/editor_plugin_src.js',
        'karl.views:static/tinymce/3.3.9.2/plugins/embedmedia/editor_plugin_src.js',
        'karl.views:static/tinymce/3.3.9.2/plugins/imagedrawer/ajaxfileupload.js',
        'karl.views:static/tinymce/3.3.9.2/plugins/imagedrawer/editor_plugin_src.js',
        'karl.views:static/tinymce/3.3.9.2/plugins/imagedrawer/langs/en.js',
        'karl.views:static/tinymce/3.3.9.2/plugins/imagedrawer/editor_plugin_src.js',
        'karl.views:static/tinymce/3.3.9.2/plugins/kaltura/js/swfobject.js',
        'karl.views:static/tinymce/3.3.9.2/plugins/kaltura/js/kcl_js/webtoolkit.md5.js',
        'karl.views:static/tinymce/3.3.9.2/plugins/kaltura/js/kcl_js/ox.ajast.js',
        'karl.views:static/tinymce/3.3.9.2/plugins/kaltura/js/kcl_js/KalturaClientBase.js',
        'karl.views:static/tinymce/3.3.9.2/plugins/kaltura/js/kcl_js/KalturaClient.js',
        'karl.views:static/tinymce/3.3.9.2/plugins/kaltura/js/kcl_js/KalturaTypes.js',
        'karl.views:static/tinymce/3.3.9.2/plugins/kaltura/js/kcl_js/KalturaVO.js',
        'karl.views:static/tinymce/3.3.9.2/plugins/kaltura/js/kcl_js/KalturaServices.js',
        'karl.views:static/tinymce/3.3.9.2/plugins/kaltura/editor_plugin_src.js',
        'karl.views:static/tinymce/3.3.9.2/plugins/kaltura/langs/en.js',
        'karl.views:static/tinymce/3.3.9.2/plugins/advimagescale/editor_plugin_src.js',
        'karl.views:static/tinymce/3.3.9.2/plugins/advlist/editor_plugin.js',
        'karl.views:static/tinymce/3.3.9.2/plugins/lists/editor_plugin.js',
        'karl.views:static/tinymce/3.3.9.2/plugins/print/editor_plugin.js',
        'karl.views:static/tinymce/3.3.9.2/plugins/table/editor_plugin.js',
        'karl.views:static/tinymce/3.3.9.2/plugins/tinyautosave/editor_plugin_src.js',
        'karl.views:static/tinymce/3.3.9.2/plugins/tinyautosave/langs/en.js',
        'karl.views:static/min/karl-ui.min.js',
        'karl.views:static/jquery-ui/jquery.ui.selectmenu.js',
        'karl.views:static/karl-plugins/karl-calendar/karl.calendar.js',
        'karl.views:static/karl.js',)
