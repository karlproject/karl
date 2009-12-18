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

from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component import queryUtility

from repoze.bfg.chameleon_zpt import get_template
from repoze.bfg.url import model_url
from repoze.bfg.security import effective_principals
from repoze.bfg.traversal import quote_path_segment

from repoze.bfg.location import lineage
from repoze.bfg.traversal import model_path
from repoze.bfg.security import authenticated_userid
from repoze.bfg.interfaces import ISettings

from repoze.lemonade.content import get_content_type
from karl.consts import countries
from karl.utils import find_catalog
from karl.utils import find_intranet
from karl.utils import find_intranets
from karl.utils import get_setting
from karl.utils import support_attachments

from karl.models.interfaces import ICommunityContent
from karl.models.interfaces import ICommunity
from karl.models.interfaces import ICommunityInfo
from karl.models.interfaces import ICatalogSearch
from karl.models.interfaces import IGridEntryInfo
from karl.models.interfaces import ITagQuery
from karl.views.interfaces import IFooter
from karl.views.interfaces import ISidebar
from karl.views.utils import get_user_home

from repoze.bfg.traversal import find_interface

import time
_start_time = int(time.time())

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
    countries = countries

    def __init__(self, context, request, page_title=None):
        self.context = context
        self.request = request
        self.snippets = get_template('templates/snippets.pt')
        self.snippets.doctype = xhtml
        self.userid = authenticated_userid(request)
        self.app_url = app_url = request.application_url
        self.profile_url = app_url + '/profiles/%s' % self.userid
        self.here_url = self.context_url = model_url(context, request)
        self.view_url = model_url(context, request, request.view_name)
        settings = queryUtility(ISettings)
        self.js_devel_mode = settings and getattr(settings,
                                                  'js_devel_mode', None)
        self.static_url = '%s/static/r%s' % (app_url, _start_time)

        # Provide a setting in the INI to fully control the entire URL
        # to the static.  This is when the proxy runs a different port
        # number, or to "pipeline" resources on a different URL path.
        full_static_path = getattr(settings, 'full_static_path', False)
        if full_static_path:
            if '%d' in full_static_path:
                full_static_path = full_static_path % _start_time
            self.static_url = full_static_path
        self.page_title = page_title
        self.system_name = get_setting(context, 'system_name', 'KARL')

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

    @property
    def user_is_staff(self):
        gn = 'group.KarlStaff'
        if self._identity is None:
            self._identity = self.request.environ.get('repoze.who.identity')
            if self._identity:
                self._isStaff = gn in self._identity.get('groups')
        return self._isStaff

    @property
    def current_intranet(self):
        """The footer needs to know what intranet the curr url is in"""
        if self._current_intranet is None:
            self._current_intranet = find_intranet(self.context)
        return self._current_intranet

    def __getitem__(self, key):
        raise ValueError, "ZPT attempted to fetch %s" % key

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
            catalog = find_catalog(self.context)
            if community is not None:
                community_path = model_path(community)
                search = getAdapter(self.context, ICatalogSearch)
                principals = effective_principals(self.request)
                self._recent_items = []
                num, docids, resolver = search(
                    limit=10,
                    path={'query': community_path},
                    allowed={'query': principals, 'operator': 'or'},
                    sort_index='modified_date',
                    reverse=True,
                    interfaces=[ICommunityContent],
                    )
                models = filter(None, map(resolver, docids))
                for model in models:
                    adapted = getMultiAdapter((model, self.request),
                                              IGridEntryInfo)
                    self._recent_items.append(adapted)

        return self._recent_items

    community_layout_fn = 'templates/community_layout.pt'
    @property
    def community_layout(self):
        macro_template = get_template(self.community_layout_fn)
        return macro_template

    anonymous_layout_fn = 'templates/anonymous_layout.pt'
    @property
    def anonymous_layout(self):
        macro_template = get_template(self.anonymous_layout_fn)
        return macro_template

    generic_layout_fn = 'templates/generic_layout.pt'
    @property
    def generic_layout(self):
        macro_template = get_template(self.generic_layout_fn)
        return macro_template

    formfields_fn = 'templates/formfields.pt'
    @property
    def formfields(self):
        macro_template = get_template(self.formfields_fn)
        return macro_template

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
        people_path = get_setting(self.context, 'people_path', 'profiles')
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
            intranets_url = model_url(intranets, request)
            for name, entry in intranets.items():
                try:
                    content_iface = get_content_type(entry)
                except ValueError:
                    continue
                href = '%s%s/' % (intranets_url, quote_path_segment(name))
                if content_iface == ICommunity:
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
            r = queryMultiAdapter((ancestor, self.request), IFooter)
            if r is not None:
                return r(self)
        # no footer exists for this context.
        return ''

    @property
    def home_url(self):
        if self._home_url is None:
            target, extra_path = get_user_home(self.context, self.request)
            self._home_url = model_url(target, self.request, *extra_path)
        return self._home_url

    @property
    def settings(self):
        return SettingsReader(self.context)

    @property
    def support_attachments(self):
        return support_attachments(self.context)

    @property
    def logo_url(self):
        logo_path = get_setting(self.context, 'logo_path', 'images/logo.gif')
        return '%s/%s' % (self.static_url, logo_path)


class SettingsReader:
    """Convenience for reading settings in templates"""
    def __init__(self, context):
        self._context = context

    def __getattr__(self, name):
        return get_setting(self._context, name)

