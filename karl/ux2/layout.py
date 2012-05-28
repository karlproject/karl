
import json

from pyramid.decorator import reify
from pyramid.renderers import get_renderer
from pyramid.security import effective_principals
from pyramid.security import has_permission
from pyramid.security import authenticated_userid
from pyramid.traversal import find_resource
from pyramid.url import resource_url
from zope.component import getMultiAdapter

from karl.consts import countries
from karl.consts import cultures
from karl.models.interfaces import ICommunityInfo
from karl.security.policy import VIEW
from karl.utils import find_community
from karl.utils import find_intranet
from karl.utils import find_site
from karl.utils import find_chatter
from karl.views.utils import get_user_date_format


class Layout(object):
    # Some configurable options that can be overriden in a view
    project_name = 'KARL'
    section_title = 'Section Title'
    page_title = 'Page Title'
    section_style = 'full'
    extra_css = ()
    extra_js = ()
    extra_css_head = ()
    extra_js_head = ()

    countries = countries
    error_message = None
    cultures = cultures

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.app_url = request.application_url
        # what if context is not traversable?
        if getattr(context, '__name__', None) is not None:
            self.context_url = request.resource_url(context)
        else:
            self.context_url = request.url
        self.portlets = []
        self.settings = settings = request.registry.settings
        self.app_url = app_url = request.application_url
        if getattr(context, '__name__', '_no_name_') != '_no_name_':
            self.here_url = resource_url(context, request)
            self.site = find_site(context)
            chatter = find_chatter(context)
            self.chatter_url = resource_url(chatter, request)
        self.current_intranet = find_intranet(context)
        self.people_url = app_url + '/' + settings.get('people_path', 'people')
        self.profiles_url = app_url + '/profiles'
        self.project_name = settings.get('system_name', 'KARL')
        self.page_title = getattr(context, 'title', 'Page Title')
        self.userid = authenticated_userid(request)
        self.tinymce_height = 400
        self.tinymce_width = 500
        self.html_id_next = 0
        self.client_components = set()

    @reify
    def devmode(self):
        """Let templates know if we are in devmode, for comments """

        sn = 'bottlecap.devmode'
        dm = self.request.registry.settings.get(sn, "false")
        return dm == "true"

    def add_portlet(self, name, *args, **kw):
        self.portlets.append((name, args, kw))

    @apply
    def show_sidebar():
        def getter(self):
            return bool(self.portlets)
        def setter(self, value):
            # allow manual override
            self.__dict__['show_sidebar'] = value
        return property(getter, setter)

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
        community = find_community(self.context)
        adapted = getMultiAdapter((community, self.request), ICommunityInfo)
        return adapted

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
        return {
            'app_url': self.app_url,
            'context_url': self.context_url,
            'karl_static_url': self.static(''),
            'chatter_url': self.chatter_url,
            'date_format': self.user_date_format,
            'tinymce_height': self.tinymce_height,
            'tinymce_width': self.tinymce_width,
            # XXX this does not belong here, but for now
            # we generate the data for some panels here.
            # The pushdowns are already moved out from this place.
            'panel_data': {
                'tagbox': {
                    'records': [
                        {
                            'count': 2,
                            'snippet': 'nondeleteable',
                            'tag': 'flyers'
                            },
                        {
                            'count': 2,
                            'snippet': 'nondeleteable',
                            'tag': 'park'
                            },
                        {
                            'count': 2,
                            'snippet': 'nondeleteable',
                            'tag': 'volunteer'
                            },
                        {
                            'count': 2,
                            'snippet': '',
                            'tag': 'un'
                            },
                        {
                            'count': 2,
                            'snippet': 'nondeleteable',
                            'tag': 'foreign_policy'
                            },
                        {
                            'count': 1,
                            'snippet': 'nondeleteable',
                            'tag': 'unsaid'
                            },
                        {
                            'count': 2,
                            'snippet': 'nondeleteable',
                            'tag': 'advocacy'
                            },
                        {
                            'count': 2,
                            'snippet': '',
                            'tag': 'zimbabwe'
                            },
                        {
                            'count': 2,
                            'snippet': 'nondeleteable',
                            'tag': 'aryeh_neier'
                            },
                    ],
                    'docid': -1352878729,
                    },
                },
            }


    extra_js_head = (
        ##'karl.views:static/ux2/google/jsapi.js',
    )

    extra_css = (
        'karl.views:static/tinymce/tinymce-3.3.9.2.karl.css',
        'karl.views:static/slick/2.0.1/slick.grid.css',
        'karl.views:static/ux2/main.css',
        )

    @property
    def extra_js(self):

        extra_js = [
            'karl.views:static/ux2/js/mustache-0.3.0.js',
            'karl.views:static/ux2/js/jquery-ui-1.9m5.min.js',
            'karl.views:static/ux2/plugins/popper-livesearch/bc-core/jquery.cookie.js',
            'karl.views:static/ux2/plugins/popper-livesearch/bc-core/jquery.ajaxmanager-3.0.7.js',
            'karl.views:static/ux2/plugins/popper-livesearch/bc-core/jquery.caret-1.0.2.min.js',
            'karl.views:static/ux2/plugins/popper-livesearch/bc-core/jquery.timeago-0.9.3.js',
            'karl.views:static/ux2/plugins/popper-livesearch/popper.livesearch.js',
            'karl.views:static/ux2/plugins/popper-tagbox/popper.tagbox.js',
            'karl.views:static/ux2/plugins/popper-pushdown/popper.pushdown.js',
            'karl.views:static/ux2/js/pushdown.js',
            'karl.views:static/ux2/js/bootstrap-dropdown.js',
            'karl.views:static/ux2/js/popper.js',
            'karl.views:static/ux2/js/bootstrap-modal.js',
            ]

        # TinyMCE
        if True:
            extra_js.extend([
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
            ])

        extra_js.extend([
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
            ])

        # SlickGrid
        if 'slickgrid' in self.client_components:
            extra_js.extend([
                'karl.views:static/slick/2.0.1/lib/jquery.event.drag-2.0.min.js',
                'karl.views:static/slick/2.0.1/lib/jquery.event.drop-2.0.min.js',
                'karl.views:static/slick/2.0.1/slick.core.js',

                #'karl.views:static/slick/2.0.1/slick.editors.js',
                #'karl.views:static/slick/2.0.1/plugins/slick.cellrangedecorator.js',
                #'karl.views:static/slick/2.0.1/plugins/slick.cellrangeselector.js',
                #'karl.views:static/slick/2.0.1/plugins/slick.cellselectionmodel.js',
                'karl.views:static/slick/2.0.1/plugins/slick.rowselectionmodel.js',
                'karl.views:static/slick/2.0.1/plugins/slick.checkboxselectcolumn.js',

                'karl.views:static/slick/2.0.1/slick.grid.js',
                'karl.views:static/slick/2.0.1/slick.dataview.js',
                'karl.views:static/slick/2.0.1/slick.groupitemmetadataprovider.js',
                'karl.views:static/karl-plugins/karl-wikitoc/karl.wikitoc.js',

                'karl.views:static/ux2/plugins/popper-gridbox/popper.gridbox.js',
                ])

        extra_js.extend([
            'karl.views:static/jquery-plugins/jquery.timeago.js',
            'karl.views:static/jquery-ui/jquery.ui.selectmenu.js',
            'karl.views:static/ux2/plugins/karl-calendar/karl.calendar.js',
            'karl.views:static/karl.js',
            'karl.views:static/ux2/karl-ux2.js',
            ])

        # multiupload
        if 'multiupload' in self.client_components:
            extra_js.extend([
                'karl.views:static/plupload/src/javascript/gears_init.js',
                'karl.views:static/plupload/src/javascript/plupload.js',
                'karl.views:static/plupload/src/javascript/plupload.gears.js',
                'karl.views:static/plupload/src/javascript/plupload.silverlight.js',
                'karl.views:static/plupload/src/javascript/plupload.flash.js',
                'karl.views:static/plupload/src/javascript/plupload.html4.js',
                'karl.views:static/plupload/src/javascript/plupload.html5.js',
                'karl.views:static/plupload/src/javascript/jquery.ui.plupload.js',
                'karl.views:static/ux2/plugins/karl-multifileupload/json2.js',
                'karl.views:static/ux2/plugins/karl-multifileupload/karl.dialog.js',
                'karl.views:static/ux2/plugins/karl-multifileupload/karl.multifileupload.js',
                ])

        return extra_js

    @property
    def head_data_json(self):
        return json.dumps(self.head_data)

    def use_microtemplates(self, names):
        self._used_microtemplate_names = names
        self._microtemplates = None
        # update head data with it
        self.head_data['microtemplates'] = self.microtemplates

    @property
    def microtemplates(self):
        """Render the whole microtemplates dictionary"""
        if getattr(self, '_microtemplates', None) is None:
            self._microtemplates = get_microtemplates(directory=_microtemplates,
                names=getattr(self, '_used_microtemplate_names', ()))
        return self._microtemplates


    def html_id(self, html_id=None, prefix='pp-'):
        """Return a sequential html id"""
        if html_id is None:
            html_id = "%s%04i" % (prefix, self.html_id_next)
            self.html_id_next += 1
        return html_id

    ALLOWED_CLIENT_COMPONENTS = ('multiupload', 'slickgrid')
    def select_client_component(self, *names):
        illegal_components = set(names).difference(self.ALLOWED_CLIENT_COMPONENTS)
        if illegal_components:
            raise RuntimeError, 'Client components %r are selected from template, but not allowed.' % \
                (list(illegal_components), )
        self.client_components.update(names)


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


def get_microtemplates(directory, names=None):

    templates = {}

    all_filenames = {}
    for _fn in os.listdir(directory):
        if _fn.endswith('.mustache'):
            name = _fn[:-9]
            fname = os.path.join(directory, _fn)
            all_filenames[name] = fname

    # XXX Names can be a list of templates that the page needs.
    # For now on, we ignore names and include all the templates we have.
    names = all_filenames.keys()

    for name in names:
        #try:
        fname = all_filenames[name]
        #except KeyError:
        #    raise "No such microtemplate %s" % name
        templates[name] = file(fname).read()

    return templates



