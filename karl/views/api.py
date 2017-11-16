# Copyright (C) 2008-2009 Open Society Institute
#               Thomas Moroz: tmoroz@sorosny.org
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License Version 2 as published
# by the Free Software Foundation.  You may not use, modify or distribute
# this program under any other version of the GNU General Public License.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import time
import os
import json

from zope.component import ComponentLookupError
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter

from pyramid.decorator import reify
from pyramid.url import resource_url
from pyramid.security import effective_principals
from pyramid.traversal import quote_path_segment

from pyramid.location import lineage
from pyramid.traversal import find_resource
from pyramid.security import authenticated_userid
from pyramid.security import has_permission
from pyramid.renderers import get_renderer

from repoze.lemonade.content import get_content_type
from repoze.lemonade.listitem import get_listitems

from karl.application import is_normal_mode
from karl.consts import countries
from karl.consts import cultures
from karl.utils import asbool
from karl.utils import find_intranet
from karl.utils import find_intranets
from karl.utils import find_site
from karl.utils import get_settings
from karl.utils import support_attachments
from karl.views.utils import convert_to_script

from karl.models.interfaces import ICommunity
from karl.models.interfaces import ICommunityInfo
from karl.models.interfaces import IGridEntryInfo
from karl.models.interfaces import IGroupSearchFactory
from karl.models.interfaces import ITagQuery
from karl.utils import find_catalog
from karl.views.adapters import DefaultFooter
from karl.views.interfaces import IFooter
from karl.views.interfaces import ISidebar
from karl.views.utils import get_user_home
from karl.views.utils import get_user_date_format

from pyramid.traversal import find_interface

xhtml = ('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" '
         '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">')

class TemplateAPI(object):
    _community_info = None
    _recent_items = None
    _identity = None
    _isStaff = None
    _intranets_info = None
    _current_intranet = None
    _home_url = None
    _snippets = None
    _start_time = int(time.time())
    countries = countries
    cultures = cultures
    _form_field_templates = None
    _livesearch_options = None
    _should_show_calendar_tab = None
    _resources = None

    def __init__(self, context, request, page_title=None):
        self.settings = get_settings() or {}
        self.site = site = find_site(context)
        self.context = context
        self.request = request
        self.userid = authenticated_userid(request)
        self.app_url = app_url = request.application_url
        self.profile_url = app_url + '/profiles/%s' % self.userid
        self.here_url = self.context_url = resource_url(context, request)
        self.view_url = resource_url(context, request, request.view_name)
        self.js_devel_mode = asbool(self.settings.get('js_devel_mode', None))
        self.read_only = not is_normal_mode(request.registry)
        self.static_url = '%s/static/%s' % (
            app_url, request.registry.settings.get('static_rev'))
        self.browser_upgrade_url = request.registry.settings.get('browser_upgrade_url', '')

        # this data will be provided for the client javascript
        self.karl_client_data = {}

        # Provide a setting in the INI to fully control the entire URL
        # to the static.  This is when the proxy runs a different port
        # number, or to "pipeline" resources on a different URL path.
        full_static_path = self.settings.get('full_static_path', False)
        if full_static_path:
            if '%d' in full_static_path:
                # XXX XXX note self._start_time is needed... and not _start_time
                # XXX XXX since this was a trivial bug, there is chance that
                # XXX XXX this actually never runs! TODO testing???
                full_static_path = full_static_path % self._start_time
            self.static_url = full_static_path
        self.page_title = page_title
        self.system_name = self.settings.get('system_name', 'KARL')
        self.user_is_admin = 'group.KarlAdmin' in effective_principals(request)
        self.can_administer = has_permission('administer', site, request)
        self.can_email = has_permission('email', site, request)
        self.admin_url = resource_url(site, request, 'admin.html')
        self.site_announcement = getattr(site, 'site_announcement', '')
        date_format = get_user_date_format(context, request)
        self.karl_client_data['date_format'] = date_format
        # XXX XXX XXX This will never work from peoples formish templates
        # XXX XXX XXX (edit_profile and derivates) because, in those form
        # XXX XXX XXX controllers, the api is instantiated from __init__,
        # XXX XXX XXX where request.form is still unset!!! (From all other
        # XXX XXX XXX formcontrollers the api is instantiated from __call__,
        # XXX XXX XXX which is why this works. A chicken-and-egg problem, really.
        if hasattr(request, 'form') and getattr(request.form, 'errors', False):
            # This is a failed form submission request, specify an error message
            self.error_message = u'Please correct the indicated errors.'

        if self.settings:
            self.kaltura_info = dict(
                enabled =  self.settings.get(
                    'kaltura_enabled', False) in ('true', 'True'),
                partner_id = self.settings.get('kaltura_partner_id', ''),
                sub_partner_id = self.settings.get(
                    'kaltura_sub_partner_id', ''),
                admin_secret = self.settings.get('kaltura_admin_secret', ''),
                user_secret = self.settings.get('kaltura_user_secret', ''),
                kcw_uiconf_id = self.settings.get(
                    'kaltura_kcw_uiconf_id', '1000741'),
                player_uiconf_id = self.settings.get(
                    'kaltura_player_uiconf_id', ''),
                player_cache_st = self.settings.get(
                    'kaltura_player_cache_st', ''),
                local_user = self.userid,
            )
            if not self.settings.get(
                'kaltura_client_session', False) in ('true', 'True'):
                # Secrets will not be sent to client, instead session is handled on the server.
                self.kaltura_info['session_url'] = app_url + '/' + 'kaltura_create_session.json'
        else:
            self.kaltura_info = dict(
                enabled = False,
                )

        # propagate the head data to the client
        d = self.karl_client_data['kaltura'] = dict(self.kaltura_info)
        # remove secrets if needed
        if 'session_url' in d:
            # server side session management, do not send secrets to client
            del d['user_secret']
            del d['admin_secret']

    @property
    def snippets(self):
        if self._snippets is None:
            r = get_renderer('templates/snippets.pt')
            self._snippets = r.implementation()
            self._snippets.doctype = xhtml
        return self._snippets

    def has_staff_acl(self, context):
        return getattr(context, 'security_state', 'inherits') == 'public'

    def is_private_in_public_community(self, context):
        """Return true if the object is private, yet located in a
        public community.
        """
        if self.community_info is None:
            return False

        community = self.community_info.context
        if context is community:
            return False
        if getattr(community, 'security_state', 'inherits') == 'public':
            return getattr(context, 'security_state', 'inherits') == 'private'
        return False

    @reify
    def user_is_staff(self):
        return 'group.KarlStaff' in effective_principals(self.request)

    @property
    def should_show_calendar_tab(self):
        """whether to show the calendar tab in the header menu

        user must be staff, and the calendar object must exist"""
        if self._should_show_calendar_tab is None:
            if not self.user_is_staff:
                self._should_show_calendar_tab = False
            else:
                calendar_path = '/offices/calendar'
                try:
                    find_resource(self.site, calendar_path)
                    self._should_show_calendar_tab = True
                except KeyError:
                    self._should_show_calendar_tab = False
        return self._should_show_calendar_tab

    @property
    def current_intranet(self):
        """The footer needs to know what intranet the curr url is in"""
        if self._current_intranet is None:
            self._current_intranet = find_intranet(self.context)
        return self._current_intranet

    @property
    def custom_css(self):
        """Get custom css from nyc intranet, if nyc intranet exists. Then
           append current intranet's if any"""
        nyc_office_path = '/offices/nyc'
        try:
            nyc_office = find_resource(self.site, nyc_office_path)
            custom_css = getattr(nyc_office, 'css', '')
        except KeyError:
            custom_css =''
        intranet = self.current_intranet
        if intranet and intranet != nyc_office:
            intranet_css = getattr(intranet, 'css', '')
            custom_css = "%s\n%s" % (custom_css, intranet_css)
        return custom_css

    def __getitem__(self, key):
        if key == 'form_field_templates':
            # Allow this, for ZPT's sake!
            return self.form_field_templates
        raise KeyError(key)

    @property
    def community_info(self):
        if self._community_info is None:
            community = find_interface(self.context, ICommunity)
            if community is not None:
                self._community_info = getMultiAdapter(
                    (community, self.request), ICommunityInfo)
        return self._community_info

    @property
    def recent_items(self):
        if self._recent_items is None:
            community = find_interface(self.context, ICommunity)
            if community is not None:
                stmt = """SELECT docid from pgtextindex
                  WHERE community_docid='%s'
                  AND content_type not in ('IInvitation',
                  'ICalendar', 'ICalendarLayer', 'ICalendarCategory',
                  'IBlog', 'ICommunityRootFolder', 'IWiki')
                  ORDER BY modification_date DESC
                  LIMIT 20"""
                catalog = find_catalog(self.context)
                index = catalog['texts']
                docids = index.get_sql_catalog_results(stmt % community.docid)
                self._recent_items = []
                for docid in docids:
                    path = catalog.document_map.address_for_docid(docid[0])
                    try:
                        model = find_resource(self.context, path)
                    except (KeyError, TypeError):
                        continue
                    if not has_permission('view', model, self.request):
                        continue
                    try:
                        adapted = getMultiAdapter((model, self.request),
                                                  IGridEntryInfo)
                    except ComponentLookupError:
                        continue
                    self._recent_items.append(adapted)

        return self._recent_items

    community_layout_fn = 'karl.views:templates/community_layout.pt'
    @property
    def community_layout(self):
        macro_template = get_renderer(self.community_layout_fn)
        return macro_template.implementation()

    anonymous_layout_fn = 'karl.views:templates/anonymous_layout.pt'
    @property
    def anonymous_layout(self):
        macro_template = get_renderer(self.anonymous_layout_fn)
        return macro_template.implementation()

    generic_layout_fn = 'karl.views:templates/generic_layout.pt'
    @property
    def generic_layout(self):
        macro_template = get_renderer(self.generic_layout_fn)
        return macro_template.implementation()

    formfields_fn = 'karl.views:templates/formfields.pt'
    @property
    def formfields(self):
        macro_template = get_renderer(self.formfields_fn)
        return macro_template.implementation()

    @property
    def form_field_templates(self):
        if self._form_field_templates is None:
            # calculate and cache value
            if hasattr(self.request, 'form'):
                self._form_field_templates =  [
                    field.widget.template for field in
                    self.request.form.allfields]
            else:
                self._form_field_templates = []
        return self._form_field_templates

    _status_message = None
    def get_status_message(self):
        if self._status_message:
            return self._status_message
        return self.request.params.get("status_message", None)

    def set_status_message(self, value):
        self._status_message = value

    status_message = property(get_status_message, set_status_message)

    _error_message = None
    def get_error_message(self):
        if self._error_message:
            return self._error_message
        return self.request.params.get("error_message", None)

    def set_error_message(self, value):
        self._error_message = value

    error_message = property(get_error_message, set_error_message)

    @property
    def people_url(self):
        # Get a setting for what part is appended the the app_url for
        # this installation's people directory application.
        people_path = self.settings.get('people_path', 'people')
        return self.app_url + "/" + people_path

    @property
    def tag_users(self):
        """Data for the tagbox display"""
        tagquery = getMultiAdapter((self.context, self.request), ITagQuery)
        return tagquery.tagusers

    @property
    def intranets_info(self):
        """Get information for the footer and intranets listing"""
        if self._intranets_info is None:
            intranets_info = []
            intranets = find_intranets(self.context)
            if not intranets:
                # Maybe there aren't any intranets defined yet
                return []
            request = self.request
            intranets_url = resource_url(intranets, request)
            for name, entry in intranets.items():
                try:
                    content_iface = get_content_type(entry)
                except ValueError:
                    continue
                if content_iface == ICommunity:
                    if not has_permission('view', entry, request):
                        continue
                    href = '%s%s/' % (intranets_url, quote_path_segment(name))
                    intranets_info.append({
                            'title': entry.title,
                            'intranet_href': href,
                            'edit_href': href + '/edit_intranet.html',
                            })
            # Sort the list
            def intranet_sort(x, y):
                if x['title'] > y['title']:
                    return 1
                else:
                    return -1
            self._intranets_info = sorted(intranets_info, intranet_sort)
        return self._intranets_info

    def actions_to_menu(self, actions):
        """A helper used by the snippets rendering the actions menu.

        This method converts the flat list of action tuples,
        passed in as input parameters, into a structured list.

        From this input::

            (
                ('Manage Members', 'manage.html'),
                ('Add Folder', 'add_folder.html'),
                ('Add File', 'add_file.html'),
                ('Add Forum', 'add_forum.html'),
            )

        it will generate a submenu structure::

            (
                ('Manage Members', 'manage.html'),
                ('Add', '#', (
                        ('Folder', 'add_folder.html'),
                        ('File', 'add_file.html'),
                        ('Forum', 'add_forum.html'),
                    )
            )

        but if there are only 2 or less groupable items, the menu
        stays flat and a submenu is not created.

        At the moment, there is no information marking the Add
        items. Therefore the following heuristics is applied:

        - if a title starts with Add, it is considered as Add item

        - the rest of the title is considered the content type.


        XXX p.s. according to this heuristics, the following will
        also be detected as an Add item::

           ('Add Existing', 'add_existing.html')

        Which won't be a problem if there is no more then 3 Add
        items altogether.
        """
        result = []
        lookahead = []
        def process_lookahead(result=result, lookahead=lookahead):
            if len(lookahead) > 2:
                # Convert to submenu
                # take part after "Add " as title.
                result.append(('Add', '#',
                    [(item[0][4:], item[1]) for item in lookahead]))
            else:
                # add to menu as flat
                result.extend(lookahead)
            # We processed it
            del lookahead[:]

        for action in actions:
            # Is this a menu action?
            is_menu_action = action[0].startswith('Add ')
            # pad them out to make sure template does not fail
            action = action + ((), )
            if is_menu_action:
                lookahead.append(action)
            else:
                # process lookahead
                process_lookahead()
                result.append(action)
        process_lookahead()
        return result

    def render_sidebar(self):
        """Render the sidebar appropriate for the context."""
        for ancestor in lineage(self.context):
            r = queryMultiAdapter((ancestor, self.request), ISidebar)
            if r is not None:
                return r(self)
        # no sidebar exists for this context.
        return ''

    def render_footer(self):
        """Render the footer appropriate for the context."""
        for ancestor in lineage(self.context):
            r = queryMultiAdapter((ancestor, self.request), IFooter,)
            if r is not None:
                return r(self)

        # no footer exists for this context, use the default.
        return DefaultFooter(self.context, self.request)(self)

    @property
    def home_url(self):
        if self._home_url is None:
            target, extra_path = get_user_home(self.context, self.request)
            self._home_url = resource_url(target, self.request, *extra_path)
        return self._home_url

    @property
    def support_attachments(self):
        return support_attachments(self.context)

    @property
    def logo_url(self):
        logo_path = self.settings.get('logo_path', 'images/logo.gif')
        return '%s/%s' % (self.static_url, logo_path)

    def render_karl_client_data(self, update_dict=None):
        """
        How to provide data to the client? There are 3 ways:

        1. specify the data via the template api

           api.karl_client_data['my_widget'] = {...my_data...}

           The code will be injected to all pages automatically.
           Be careful not to overwrite api.karl_client_data, only update
           one or more fields of the dictionary.


        2. Pass the data directly to the template

           render_template_to_response(...
                ...
                karl_client_data = {'my_widget': {...my_data...}},
                ...)

            The passed dictionary will update the one specified via the template api.


        3. Legacy way: head_data


           from karl.views.utils import convert_to_script

           render_template_to_response(...
                ...
                head_data = convert_to_script({'my_widget': {...my_data...}),
                ...)

           Data inserted this way is supported in order to not break old code, but for
           new code please prefer to use the methods described in point 1. or 2.

        """
        d = dict(self.karl_client_data)
        if update_dict:
            d.update(update_dict)
        return convert_to_script(d, var_name='karl_client_data')

    @property
    def livesearch_options(self):
        if self._livesearch_options is None:
            self._livesearch_options = [
                item for item in get_listitems(IGroupSearchFactory )
                if item['component'].livesearch]
        return self._livesearch_options

    @property
    def is_js_devel_mode(self):
        return self.js_devel_mode == 'true' or self.js_devel_mode == 'True' or self.js_devel_mode == True

    @property
    def resources(self):
        # never cache in devmode.
        if self.is_js_devel_mode or self._resources is None:
            path = os.path.join(os.path.dirname(__file__), 'static', 'resources.json')
            self._resources = json.load(open(path))
        return self._resources

    def resource_js(self, name):
        try:
            files = self.resources['js'][name]
        except KeyError:
            raise RuntimeError, 'JS resource "%s" must be defined as a key in resources.json.'
        if self.is_js_devel_mode:
            result = ['%s/%s' % (self.static_url, n) for n in files]
        else:
            if name.startswith('tinymce'):
                prefix = self.resources['tinymceMinPrefix']
            else:
                prefix = self.resources['minPrefix']
            result = ['%s/%s%s.min.js' % (self.static_url, prefix, name)]
        return result

    def resource_css(self, name):
        if name not in self.resources['css']:
            raise RuntimeError, 'CSS resource "%s" must be defined as a key in resources.json.'
        if name.startswith('tinymce'):
            prefix = 'tinymce/'
        else:
            prefix = ''
        if self.is_js_devel_mode:
            result = '%s/%s%s.css' % (self.static_url, prefix, name)
        else:
            result = '%s/%s%s.min.css' % (self.static_url, prefix, name)
        return result
