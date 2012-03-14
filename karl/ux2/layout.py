
import copy
from bottlecap.layouts.popper.layout import PopperLayout
from bottlecap.layouts.popper.layout import get_microtemplates

from pyramid.decorator import reify
from pyramid.renderers import get_renderer
from pyramid.security import effective_principals
from pyramid.security import has_permission
from pyramid.security import authenticated_userid
from pyramid.traversal import find_resource
from pyramid.url import resource_url

from karl.consts import countries
from karl.consts import cultures
from karl.security.policy import VIEW
from karl.utils import find_community
from karl.utils import find_intranet
from karl.utils import find_site
from karl.utils import find_chatter
from karl.views.utils import get_user_date_format


class Layout(PopperLayout):
    countries = countries
    error_message = None
    cultures = cultures

    def __init__(self, context, request):
        super(Layout, self).__init__(context, request)
        self.settings = settings = request.registry.settings

        self.app_url = app_url = request.application_url
        self.here_url = resource_url(context, request)
        self.current_intranet = find_intranet(context)
        self.people_url = app_url + '/' + settings.get('people_path', 'people')
        self.site = find_site(context)
        chatter = find_chatter(context)
        self.chatter_url = resource_url(chatter, request)
        self.project_name = settings.get('system_name', 'KARL')
        self.page_title = getattr(context, 'title', 'Page Title')
        self.userid = authenticated_userid(request)

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

    @reify
    def community(self):
        return find_community(self.context)

    @apply
    def section_title():
        def getter(self):
            community = self.community
            if community:
                title = community.title
            else:
                title = 'Section Title'  # annoying default to spur override
            self.__dict__['title'] = title  # reify
            return title

        def setter(self, title):
            self.__dict__['title'] = title  # reify

        return property(getter, setter)

    def is_private_in_public_community(self, context=None):
        if context is None:
            context = self.context
        community = self.community
        if not community or context is community:
            return False
        if getattr(community, 'security_state', 'inherits') == 'public':
            return getattr(context, 'security_state', 'inherits') == 'private'
        return False

    @reify
    def user_date_format(self):
        return get_user_date_format(self.context, self.request)

    @reify
    def head_data(self):
        head_data = super(Layout, self).head_data
        head_data = copy.deepcopy(head_data)
        head_data.update({
            # Add some more stuff to the head_data factorized by popper
            'karl_static_url': self.static(''),
            'chatter_url': self.chatter_url,
            'date_format': self.user_date_format,
        })
        return head_data

    extra_js_head = (
        'https://www.google.com/jsapi',
    )

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

        ##'karl.views:static/min/karl-ui.min.js',
        # This original combo has to be split up, as it contains code
        # already ported to popper (eg. livesearch) or used from there (eg. jquery)
        #
        # JQuery and JQuery-UI:
        #    jquery/jquery-1.4.4.js
        #    min/jquery-ui-1.9m3.karl.js
        #
        # Additional JQuery-UI:
            'karl.views:static/jquery-ui/grid/ui/ui.grid.js',
            'karl.views:static/jquery-ui/grid/ui/ui.gridmodel.js',
            # XXX we don't use autobox any more, but we keep it for a while
            # because karl.js depends on it.
            'karl.views:static/jquery-ui/autobox2/jquery.templating.js',
            'karl.views:static/jquery-ui/autobox2/jquery.ui.autobox.ext.js',
            'karl.views:static/jquery-ui/autobox2/jquery.ui.autobox.js',
        #
        # KARL plugins:
            'karl.views:static/karl-plugins/karl-multistatusbox/karl.multistatusbox.js',
            'karl.views:static/karl-plugins/karl-captionedimage/karl.captionedimage.js',
            'karl.views:static/karl-plugins/karl-slider/karl.slider.js',
            'karl.views:static/karl-plugins/karl-buttonset/karl.buttonset.js',
        #
        # Additional JQuery plugins:
            'karl.views:static/jquery-plugins/jquery.scrollTo.src.js',
            'karl.views:static/jquery-plugins/jquery.tools.js',
        #
        # Bottlecap livesearch:
        #   bottlecap-wire/livesearch-all.js
        #
        #  i10n: (Now relocated to ux2)
            'karl.views:static/ux2/l10n/globalize.js',
            'karl.views:static/ux2/l10n/globalize.cultures.js',
            'karl.views:static/ux2/l10n/globalize.actions.js',
        #
        # END of this original combo
        ## 'karl.views:static/min/karl-ui.min.js',

        #
        'karl.views:static/jquery-ui/jquery.ui.selectmenu.js',
        'karl.views:static/karl-plugins/karl-calendar/karl.calendar.js',
        'karl.views:static/karl.js',
        'karl.views:static/ux2/karl-ux2.js',
        )

    @property
    def microtemplates(self):
        """Render the whole microtemplates dictionary
        Take popper's templates and allow them to overriden locally.
        """
        if getattr(self, '_microtemplates', None) is None:
            self._microtemplates = super(Layout, self).microtemplates
            self._microtemplates.update(get_microtemplates(directory=_microtemplates,
                names=getattr(self, '_used_microtemplate_names', ())))
        return self._microtemplates


class ProfileLayout(Layout):
    section_style = 'none'


class PeopleDirectoryLayout(Layout):
    section_style = 'compact'

class ChatterLayout(Layout):
    section_style = 'compact'

# FIXME Use pkg_resources
import os
_here = os.path.dirname(__file__)
_microtemplates = os.path.join(_here, 'microtemplates')



