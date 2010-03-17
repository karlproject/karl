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

from lxml.html.clean import clean_html
import formish
import schemaish
from validatish import validator
from karl.content.interfaces import IIntranetRootFolder
from karl.events import ObjectModifiedEvent
from karl.events import ObjectWillBeModifiedEvent
from karl.models.interfaces import ICommunity
from karl.models.interfaces import IIntranet
from karl.models.interfaces import IToolFactory
from karl.utils import find_community
from karl.utils import find_users
from karl.utils import get_layout_provider
from karl.views.api import TemplateAPI
from karl.views.community import EditCommunityFormController
from karl.views.forms import validators as karlvalidators
from karl.views.utils import make_name
from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.formish import ValidationError
from repoze.bfg.security import authenticated_userid
from repoze.bfg.url import model_url
from repoze.lemonade.content import create_content
from repoze.lemonade.listitem import get_listitems
from webob.exc import HTTPFound
from zope.component.event import objectEventNotify
from zope.interface import alsoProvides

def show_intranets_view(context, request):

    page_title = context.title
    api = TemplateAPI(context, request, page_title)

    actions = [
        ('Add Intranet', 'add_intranet.html'),
        ]


    return render_template_to_response(
        'templates/show_intranets.pt',
        api=api,
        actions=actions,
        intranets_info=api.intranets_info,
        )

def split_lines(lines):
    """
    Splits the provided text value by line breaks, strips each result,
    and returns a list of the non-empty results.
    """
    result = []
    for line in lines.split('\r'):
        stripped = line.strip()
        if stripped:
            result.append(line)
    return result

# title and/or name field require name checking validation,
# but this is happening in handle_submit b/c it requires a
# bit of extra logic
title_field = schemaish.String(validator=validator.Required())
name_field = schemaish.String(
    description="Short name that will be part of the URL for "
    "this Intranet.  Will be auto-generated from the Title if "
    "left blank.")
address_field = schemaish.String()
city_field = schemaish.String()
state_field = schemaish.String()
country_field = schemaish.String()
zipcode_field = schemaish.String()
telephone_field = schemaish.String()
navigation_field = schemaish.String(title='Navigation Menu',
                                    description="Paste HTML structured according "
                                    "to the navigation menu format rules.  Leave "
                                    "empty for an example.",
                                    validator=karlvalidators.HTML())
middle_portlets_field = schemaish.String(
    description="Sequence of portlet identifiers for the middle column, one per "
    "line.")
right_portlets_field = schemaish.String(
    description="Sequence of portlet identifiers for the right column, one per "
    "line.")

class AddIntranetFormController(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        page_title = getattr(self, 'page_title', 'Add Intranet')
        self.api = TemplateAPI(context, request, page_title)

    def form_fields(self):
        fields = [('title', title_field),
                  ('name', name_field),
                  ('address', address_field),
                  ('city', city_field),
                  ('state', state_field),
                  ('country', country_field),
                  ('zipcode', zipcode_field),
                  ('telephone', telephone_field),
                  ('navigation', navigation_field),
                  ('middle_portlets', middle_portlets_field),
                  ('right_portlets', right_portlets_field),
                  ]
        return fields

    def form_widgets(self, fields):
        widgets = {'navigation': formish.TextArea(rows=10, cols=80),
                   'middle_portlets': formish.TextArea(rows=10, cols=80),
                   'right_portlets': formish.TextArea(rows=10, cols=80),
                   }
        return widgets

    def __call__(self):
        api = self.api
        layout_provider = get_layout_provider(self.context, self.request)
        layout = layout_provider('community')
        return {'api': api, 'layout': layout, 'actions': []}

    def handle_cancel(self):
        return HTTPFound(location=model_url(self.context, self.request))

    def handle_submit(self, converted):
        request = self.request
        context = self.context

        intranets_parent = find_community(context)
        name = converted.get('name')
        if name:
            name_from = 'name'
        else:
            name = converted['title']
            name_from = 'title'
        try:
            name = make_name(intranets_parent, name)
        except ValueError, why:
            msg = why[0]
            raise ValidationError(**{name_from: msg})

        userid = authenticated_userid(request)
        community = create_content(ICommunity,
                                   converted['title'],
                                   u'',
                                   u'',
                                   userid,
                                   )
        if not converted['navigation']:
            converted['navigation'] = sample_navigation
        if converted['middle_portlets']:
            middle_portlets = split_lines(converted['middle_portlets'])
        else:
            middle_portlets = sample_middle_portlets
        if converted['right_portlets']:
            right_portlets = split_lines(converted['right_portlets'])
        else:
            right_portlets = sample_right_portlets

        # Jam on the other data
        community.address = converted['address']
        community.city = converted['city']
        community.state = converted['state']
        community.country = converted['country']
        community.zipcode = converted['zipcode']
        community.telephone = converted['telephone']
        community.navigation = clean_html(converted['navigation'])
        community.middle_portlets = middle_portlets
        community.right_portlets = right_portlets

        # required to use moderators_group_name and
        # members_group_name
        community.__name__ = name

        for toolinfo in get_listitems(IToolFactory):
            if toolinfo['name'] in ('forums', 'files'):
                toolinfo['component'].add(community, request)

        # Jam on the second interface IIntranet so we can attach
        # any other views to it.  Ditto for IIntranetRootFolder.
        alsoProvides(community, IIntranet)
        files = community.get('files', False)
        if files:
            alsoProvides(files, IIntranetRootFolder)

        users = find_users(context)
        moderators_group_name = community.moderators_group_name
        members_group_name = community.members_group_name

        for group_name in moderators_group_name, members_group_name:
            users.add_group(userid, group_name)

        # This subcommunity (intranet) gets added directly in the
        # parent, not in a tool subfolder.  E.g. store it in /osi.
        intranets_parent = find_community(context)
        intranets_parent[name] = community

        # Adding a community should take you to the Add Existing
        # User screen, so the moderator can include some users.
        location = model_url(context, request)
        location = location + "?status_message=Intranet%20added"

        return HTTPFound(location=location)

class EditIntranetFormController(AddIntranetFormController):
    def __init__(self, context, request):
        self.page_title = 'Edit %s' % context.title
        super(EditIntranetFormController, self).__init__(context, request)

    def form_fields(self):
        fields = [('title', title_field),
                  ('address', address_field),
                  ('city', city_field),
                  ('state', state_field),
                  ('country', country_field),
                  ('zipcode', zipcode_field),
                  ('telephone', telephone_field),
                  ('navigation', navigation_field),
                  ('middle_portlets', middle_portlets_field),
                  ('right_portlets', right_portlets_field),
                  ]
        return fields

    def form_defaults(self):
        context = self.context
        defaults = {'title': context.title,
                    'address': context.address,
                    'city': context.city,
                    'state': context.state,
                    'country': context.country,
                    'zipcode': context.zipcode,
                    'telephone': context.telephone,
                    'navigation': context.navigation,
                    'middle_portlets': '\r'.join(context.middle_portlets),
                    'right_portlets': '\r'.join(context.right_portlets),
                    }
        return defaults

    def __call__(self):
        api = self.api
        layout_provider = get_layout_provider(self.context, self.request)
        layout = layout_provider('generic')
        return {'api': api, 'layout': layout, 'actions': []}

    def handle_submit(self, converted):
        request = self.request
        context = self.context
        # *will be* modified event
        objectEventNotify(ObjectWillBeModifiedEvent(context))
        if converted.get('middle_portlets'):
            middle_portlets = split_lines(converted['middle_portlets'])
        else:
            middle_portlets = []
        if converted.get('right_portlets'):
            right_portlets = split_lines(converted['right_portlets'])
        else:
            right_portlets = []
        context.title = converted['title']
        context.address = converted['address']
        context.city = converted['city']
        context.state = converted['state']
        context.country = converted['country']
        context.zipcode = converted['zipcode']
        context.telephone = converted['telephone']
        context.navigation = clean_html(converted['navigation'])
        context.middle_portlets = middle_portlets
        context.right_portlets = right_portlets
        # *modified* event
        objectEventNotify(ObjectModifiedEvent(context))
        
        location = model_url(context.__parent__['intranets'], request)
        return HTTPFound(location=location)

feature_field = schemaish.String(
    description="Paste HTML for the feature block on the intranet "
    "home pages. Leave empty for an example.",
    validator=karlvalidators.HTML())

class EditIntranetRootFormController(EditCommunityFormController):
    """
    Adds a 'feature' field to the default community schema.
    """
    def __init__(self, context, request):
        parent = self.parent = super(EditIntranetRootFormController, self)
        parent.__init__(context, request)

    def form_defaults(self):
        defaults = self.parent.form_defaults()
        defaults['feature'] = self.context.feature
        return defaults

    def form_fields(self):
        fields = self.parent.form_fields()
        fields.insert(4, ('feature', feature_field))
        return fields

    def form_widgets(self, fields):
        widgets = self.parent.form_widgets(fields)
        widgets['feature'] = formish.TextArea(rows=10, cols=80, empty='')
        return widgets

    def __call__(self):
        context = self.context
        page_title = "Edit %s" % context.title
        api = TemplateAPI(context, self.request, page_title)
        return {'api': api, 'actions': ()}

    def handle_submit(self, converted):
        """
        Have to copy this code from the base class so the events will
        fire at the right time.
        """
        context = self.context
        request = self.request
        objectEventNotify(ObjectWillBeModifiedEvent(context))
        workflow = self.workflow
        if workflow is not None:
            if 'security_state' in converted:
                workflow.transition_to_state(context, request,
                                             converted['security_state'])
        context.title = converted['title']
        context.description = converted['description']
        context.text = converted['text']
        context.feature = clean_html(converted['feature'])
        # NB: this is an edit form, so tags are added immediately via
        # AJAX; we needn't deal with setting them in the form post
        tools_present = [None]
        available_tools = self.available_tools
        for info in available_tools:
            component = info['component']
            tool_name = info['name']
            tools_present.append(tool_name)
            present = component.is_present(context, request)
            if (not present) and tool_name in converted['tools']:
                component.add(context, request)
            if present and (tool_name not in converted['tools']):
                component.remove(context, request)
                tools_present.remove(tool_name)
        if converted['default_tool'] in tools_present:
            context.default_tool = converted['default_tool']
        elif not (context.default_tool in tools_present):
            context.default_tool = None

        # *modified* event
        objectEventNotify(ObjectModifiedEvent(context))
        location = model_url(context, request)
        return HTTPFound(location=location)
        

sample_middle_portlets = ['network-news', 'network-events', 'interesting-feed']
sample_right_portlets = ['my-site-news', 'my-site-personals']

sample_feature = """\
<div>
  <div class="teaser">
    <a href="#">
      <img src="/static/images/sample_feature.jpg"/>
    </a>
  </div>
  <div class="visualClear"> </div>
  <div class="featureLinks">
    <p>
      <a href="#">Read the latest SFN Advocacy Newsletter</a>
    </p>
    <p>
      <a href="#">Read the latest Newsletter</a>
    </p>
  </div>
</div>
"""

sample_navigation = """\
<div>
	<div class="menu">
          <h3>About Our Sample Organization</h3>
          <ul class="nav">
            <li><a href="#">About Our Network</a></li>
            <li><a href="#">About Us</a></li>
            <li><a href="#">Network Directory</a></li>
          </ul>
	</div>
	<div class="menu">
          <h3>Resources</h3>
          <ul class="nav">
            <li class="submenu">
              <a href="#">Administration</a>
              <ul class="level2">
		<li><a href="#">Communications</a></li>
		<li><a href="#">Facilities Management</a></li>
		<li><a href="#">Finance</a></li>
		<li><a href="#">Legal</a></li>
		<li><a href="#">Grants Management</a></li>
		<li><a href="#">Human Resources</a></li>
		<li><a href="#">Information Systems</a></li>
		<li><a href="#">Records Management</a></li>
		<li><a href="#">Travel Authorization and Security</a></li>
		<li><a href="#">Travel and Expenses</a></li>
              </ul>
            </li>
            <li><a href="#">What's for Lunch?</a></li>
            <li><a href="#">Holiday Schedule</a></li>
            <li><a href="#">Message Boards</a></li>
          </ul>
	</div>
	<div class="menu">
          <h3>Tools &amp; Services</h3>
          <ul class="nav">
            <li><a href="#">Business Center</a></li>
            <li class="submenu"><a href="#">Meeting Calendar</a>
              <ul class="level2">
		<li><a href="#">Calendar of Events</a></li>
		<li><a href="#">Today's Events</a></li>
		<li><a href="#">Reserve a Room</a></li>
		<li><a href="#">Meeting Planner</a></li>
              </ul>
            </li>
            <li><a href="#">Web Requests</a></li>
            <li><a href="#">Hardware/Software Requests</a></li>
            <li><a href="#">Travel Requests</a></li>
            <li class="submenu">
              <a href="#">Research &amp; Reference</a>
              <ul class="level2">
		<li><a href="#">Library Databases</a></li>
		<li><a href="#">SNAP</a></li>
              </ul>
            </li>
            <li><a href="#">Interaction</a></li>
          </ul>
	</div>
	<div class="menu">
          <h3>Help Desk</h3>
          <ul class="nav">
            <li><a href="#">Trouble Ticket</a></li>
            <li class="submenu">
              <a href="#">Phone &amp; Voicemail</a>
              <ul class="level2">
		<li><a href="#">Using Voicemail</a></li>
		<li><a href="#">Using Telephone</a></li>
		<li><a href="#">Conference Call Reservations</a></li>
		<li><a href="#">UMS, Unified Messaging</a></li>
              </ul>
            </li>
            <li><a href="#">Checking Webmail</a></li>
            <li class="submenu">
              <a href="#">Login &amp; Password</a>
              <ul class="level2">
		<li><a href="#">Login help</a></li>
		<li><a href="#">Changing Password</a></li>
              </ul>
            </li>
            <li><a href="#">Karl User Manual</a></li>
          </ul>
	</div>
      </div>
"""
