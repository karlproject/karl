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

from formencode import Invalid
from karl.content.interfaces import IIntranetRootFolder
from karl.events import ObjectModifiedEvent
from karl.events import ObjectWillBeModifiedEvent
from karl.models.interfaces import ICommunity
from karl.models.interfaces import IIntranet
from karl.models.interfaces import ITagQuery
from karl.models.interfaces import IToolFactory
from karl.security.workflow import get_security_states
from karl.utils import find_community
from karl.utils import find_users
from karl.utils import get_setting
from karl.views.adapters import DefaultToolAddables
from karl.views.api import TemplateAPI
from karl.views.form import render_form_to_response
from karl.views.interfaces import IToolAddables
from karl.views.tags import set_tags
from karl.views.utils import convert_to_script
from karl.views.utils import make_name
from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.security import authenticated_userid
from repoze.bfg.url import model_url
from repoze.workflow import get_workflow
from repoze.enformed import FormSchema
from repoze.lemonade.content import create_content
from repoze.lemonade.listitem import get_listitems
from urllib import quote
from webob.exc import HTTPFound
from zope.component.event import objectEventNotify
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
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


def add_intranet_view(context, request):

    system_name = get_setting(context, 'system_name', 'KARL')
    form = AddIntranetForm()

    if 'form.cancel' in request.POST:
        return HTTPFound(location=model_url(context, request))

    if 'form.submitted' in request.POST:
        try:
            converted = form.validate(request.POST)
            # Now add the intranet community
            name = converted.get('name')
            if not name:
                name = converted['title']
            try:
                name = make_name(context, name)
            except ValueError, why:
                location = model_url(context, request, request.view_name)
                msg = why[0]
                location = location + "?status_message=" + quote(msg)
                return HTTPFound(location=location)

            userid = authenticated_userid(request)

            community = create_content(ICommunity,
                                       converted['title'],
                                       u'',
                                       u'',
                                       userid,
                                       )

            # If some of the fields were empty, jam in an example, as
            # it is a bit cryptic.
            if converted['navigation'] == u'':
                converted['navigation'] = sample_navigation
            if converted['middle_portlets'] == u'':
                converted['middle_portlets'] = sample_middle_portlets
            if converted['right_portlets'] == u'':
                converted['right_portlets'] = sample_right_portlets

            # Jam on the other data
            community.address = converted['address']
            community.city = converted['city']
            community.state = converted['state']
            community.country = converted['country']
            community.zipcode = converted['zipcode']
            community.telephone = converted['telephone']
            community.navigation = converted['navigation']
            community.middle_portlets = converted['middle_portlets']
            community.right_portlets = converted['right_portlets']

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

        except Invalid, e:
            fielderrors = e.error_dict
            fill_values = form.convert(request.POST)

    else:
        fielderrors = {}
        fill_values = {}

    # Render the form and shove some default values in
    page_title = 'Add Intranet'
    api = TemplateAPI(context, request, page_title)

    return render_form_to_response(
        'templates/add_intranet.pt',
        form,
        fill_values,
        post_url=request.url,
        formfields=api.formfields,
        fielderrors=fielderrors,
        api=api,
        system_name=system_name,
        )


def edit_intranet_view(context, request):
    system_name = get_setting(context, 'system_name', 'KARL')
    form = EditIntranetForm()

    if 'form.cancel' in request.POST:
        return HTTPFound(location=model_url(context.__parent__['intranets'],
                                            request))

    if 'form.submitted' in request.POST:
        try:
            converted = form.validate(request.POST)
            # *will be* modified event
            objectEventNotify(ObjectWillBeModifiedEvent(context))
            context.title = converted['title']
            context.address = converted['address']
            context.city = converted['city']
            context.state = converted['state']
            context.country = converted['country']
            context.zipcode = converted['zipcode']
            context.telephone = converted['telephone']
            context.navigation = converted['navigation']
            context.middle_portlets = converted['middle_portlets']
            context.right_portlets = converted['right_portlets']

            # *modified* event
            objectEventNotify(ObjectModifiedEvent(context))

            location = model_url(context.__parent__['intranets'], request)
            return HTTPFound(location=location)

        except Invalid, e:
            fielderrors = e.error_dict
            fill_values = form.convert(request.POST)

    else:
        fielderrors = {}
        fill_values = dict(
            title = context.title,
            address = context.address,
            city = context.city,
            state = context.state,
            country = context.country,
            zipcode = context.zipcode,
            telephone = context.telephone,
            navigation = context.navigation,
            middle_portlets = context.middle_portlets,
            right_portlets = context.right_portlets,
            )


    page_title = 'Edit ' + context.title
    api = TemplateAPI(context, request, page_title)

    return render_form_to_response(
        'templates/edit_intranet.pt',
        form,
        fill_values,
        post_url=request.url,
        formfields=api.formfields,
        fielderrors=fielderrors,
        form=form,
        api=api,
        system_name=system_name,
        )


def edit_intranet_root_view(context, request):
    # context is an ICommunity that also provides IIntranets.

    # Note that this form probably provides a lot of features no one
    # needs. Yuck.

    tags_list = request.POST.getall('tags')
    form = EditIntranetRootForm(tags_list=tags_list)
    workflow = get_workflow(ICommunity, 'security', context)
    available_tools = queryMultiAdapter(
        (context, request), IToolAddables,
        default=DefaultToolAddables(context, request))()

    if workflow is None:
        security_states = []
    else:
        security_states = get_security_states(workflow, context, request)

    if security_states:
        form.add_field('security_state', baseforms.security_state)

    if 'form.cancel' in request.POST:
        return HTTPFound(location=model_url(context, request))

    if 'form.submitted' in request.POST:
        try:
            converted = form.validate(request.POST)
            # *will be* modified event
            objectEventNotify(ObjectWillBeModifiedEvent(context))
            if workflow is not None:
                if 'security_state' in converted:
                    workflow.transition_to_state(context, request,
                                                 converted['security_state'])

            context.title = converted['title']
            context.description = converted['description']
            context.text = converted['text']
            context.default_tool = request.params['default_tool']
            context.feature = converted['feature'] or sample_feature

            # Save the tags on it
            set_tags(context, request, converted['tags'])

            for info in available_tools:
                component = info['component']
                present = component.is_present(context, request)
                if (not present) and info['name'] in request.params:
                    component.add(context, request)
                if present and (info['name'] not in request.params):
                    component.remove(context, request)

            # *modified* event
            objectEventNotify(ObjectModifiedEvent(context))

            location = model_url(context, request)
            return HTTPFound(location=location)

        except Invalid, e:
            fielderrors = e.error_dict
            fill_values = form.convert(request.POST)
            # Get the default list of tools into sequence of dicts AND
            # set checked state based on what the user typed in before
            # invalidation.
            tools = []
            default_tools = [
                {'title': 'Overview', 'name': '',
                 'selected': (not context.default_tool)},
                ]
            for info in available_tools:
                state = request.params.has_key(info['name'])
                tools.append(
                    {'name': info['name'], 'title': info['title'],
                     'state': state}
                    )
                if info['component'].is_present(context, request):
                    # Add this to the list of choices for
                    # default_tool, but first find out if it should be
                    # selected.
                    selected = False
                    if request.params['default_tool'] == info['name']:
                        selected = True
                    elif context.default_tool == info['name']:
                        selected = True
                    default_tools.append(
                        {'name': info['name'], 'title': info['title'],
                         'selected': selected}
                        )

            # provide client data for rendering current tags in the tagbox.
            # We arrived here because the form is invalid.
            tagbox_records = [dict(tag=tag) for tag in
                              request.POST.getall('tags')]
            # We still need the adapter for the docid
            # (XXX or, could we get docid without the adapter?)
            tagquery = getMultiAdapter((context, request), ITagQuery)
            tagbox_docid = tagquery.docid

    else:
        fielderrors = {}
        if workflow is None:
            security_state = ''
        else:
            security_state = workflow.state_of(context)
        fill_values = dict(
            title=context.title,
            description=context.description,
            text=context.text,
            feature=getattr(context, 'feature', sample_feature),
            security_state = security_state,
            )

        # Get the default list of tools into a sequence of dicts
        tools = []
        default_tools = [
            {'title': 'Overview', 'name': '',
             'selected': (not context.default_tool)},
            ]
        for info in available_tools:
            component = info['component']
            present = component.is_present(context, request)
            tools.append(
                {'name': info['name'], 'title': info['title'],
                 'state': present}
                )
            if present:
                default_tools.append(
                    {'name': info['name'], 'title': info['title'],
                     'selected': (context.default_tool == info['name'])}
                     )

        # provide client data for rendering current tags in the tagbox.
        tagquery = getMultiAdapter((context, request), ITagQuery)
        tagbox_docid = tagquery.docid
        tagbox_records = tagquery.tagswithcounts

    # prepare client data
    client_json_data = dict(
        tags_field = dict(
            records = tagbox_records,
            docid = tagbox_docid,
            ),
    )

    page_title = 'Edit ' + context.title
    api = TemplateAPI(context, request, page_title)

    return render_form_to_response(
        'templates/edit_intranet_root.pt',
        form,
        fill_values,
        post_url=request.url,
        formfields=api.formfields,
        fielderrors=fielderrors,
        tools=tools,
        default_tools=default_tools,
        form=form,
        api=api,
        head_data=convert_to_script(client_json_data),
        security_states = security_states,
        )


# Forms
from formencode import validators
from karl.views import baseforms
class AddIntranetForm(FormSchema):
    title = baseforms.title
    name = validators.UnicodeString(strip=True)
    address = validators.UnicodeString(strip=True)
    city = validators.UnicodeString(strip=True)
    state = validators.UnicodeString(strip=True)
    country = validators.UnicodeString(strip=True)
    zipcode = validators.UnicodeString(strip=True)
    telephone = validators.UnicodeString(strip=True)
    navigation = baseforms.HTMLValidator(strip=True)
    middle_portlets = baseforms.TextAreaToList(strip=True)
    right_portlets = baseforms.TextAreaToList(strip=True)

class EditIntranetForm(FormSchema):
    title = baseforms.title
    address = validators.UnicodeString(strip=True)
    city = validators.UnicodeString(strip=True)
    state = validators.UnicodeString(strip=True)
    country = validators.UnicodeString(strip=True)
    zipcode = validators.UnicodeString(strip=True)
    telephone = validators.UnicodeString(strip=True)
    navigation = baseforms.HTMLValidator(strip=True)
    middle_portlets = baseforms.TextAreaToList(strip=True)
    right_portlets = baseforms.TextAreaToList(strip=True)

class EditIntranetRootForm(FormSchema):
    title = baseforms.title
    tags = baseforms.tags
    description = baseforms.description
    text = validators.UnicodeString(strip=True)
    feature = baseforms.HTMLValidator(strip=True)


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

sample_middle_portlets = ['network-news', 'network-events', 'intresting-feed']
sample_right_portlets = ['my-site-news', 'my-site-personals']
