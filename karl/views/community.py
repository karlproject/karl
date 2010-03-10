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

import karl.mail

import schemaish
import formish
from validatish import validator

from repoze.lemonade.content import create_content

from zope.component.event import objectEventNotify
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component import getUtility
from zope.interface import implements
from webob.exc import HTTPFound

from repoze.bfg.chameleon_zpt import get_template
from repoze.bfg.chameleon_zpt import render_template
from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.security import authenticated_userid
from repoze.bfg.security import effective_principals
from repoze.bfg.security import has_permission
from repoze.bfg.traversal import model_path
from repoze.bfg.url import model_url

from repoze.sendmail.interfaces import IMailDelivery

from karl.events import ObjectWillBeModifiedEvent
from karl.events import ObjectModifiedEvent

from karl.models.interfaces import ICommunity
from karl.models.interfaces import ICommunityContent
from karl.models.interfaces import IGridEntryInfo
from karl.models.interfaces import ITagQuery

from repoze.workflow import get_workflow

from karl.utils import get_layout_provider
from karl.utils import find_profiles
from karl.utils import find_users

from karl.views.adapters import DefaultToolAddables
from karl.views.api import TemplateAPI
from karl.views.interfaces import ISidebar
from karl.views.interfaces import IToolAddables
from karl.views.utils import convert_to_script
from karl.views.utils import make_name
from karl.views.batch import get_catalog_batch_grid
from karl.views.tags import get_tags_client_data
from karl.views.tags import set_tags

from karl.views.forms import widgets as karlwidgets
from karl.views.forms import validators as karlvalidators

from karl.security.workflow import get_security_states

security_field = schemaish.String(
    description=('Items marked as private can only be seen by '
                 'members of this community.'))

tags_field = schemaish.Sequence(schemaish.String())

description_field = schemaish.String(
    description=('This description will appear in search results and '
                 'on the community listing page.  Please limit your '
                 'description to 100 words or less'),
    validator=validator.All(validator.Length(max=500),
                                    validator.Required())
    )

text_field =  schemaish.String(
    description=('This text will appear on the Overview page for this '
                 'community.  You can use this to describe the '
                 'community or to make a special announcement.'))

tools_field = schemaish.Sequence(
    attr=schemaish.String(),
    description = 'Select which tools to enable on this community.')

default_tool_field = schemaish.String(
    description=(
        'This is the first page people see when they view this '
        'community.'))

def shared_fields():
    return [
        ('tags', tags_field),
        ('description', description_field),
        ('text', text_field),
        ('tools', tools_field)
        ]

def shared_widgets(context):
    return {
        'title':formish.Input(empty=''),
        'description': formish.TextArea(cols=60, rows=10, empty=''),
        'text':karlwidgets.RichTextWidget(empty=''),
        'tools':formish.CheckboxMultiChoice(options=context.tools)
        }

def get_available_tools(context, request):
    available_tools = []
    available_tools = queryMultiAdapter(
        (context, request), IToolAddables,
        default=DefaultToolAddables(context, request))()
    return available_tools

class AddCommunityFormController(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.workflow = get_workflow(ICommunity, 'security', context)
        self.available_tools = get_available_tools(context, request)
        self.tools = [ (x['name'], x['title']) for x in self.available_tools ]

    def form_defaults(self):
        defaults = {
        'title':'',
        'tags': [],
        'description':'',
        'text':'',
        'tools':[ t[0] for t in self.tools ],
        }
        if self.workflow is not None:
            defaults['security_state']  = self.workflow.initial_state
        return defaults

    def form_fields(self):
        fields = shared_fields()
        title_field = schemaish.String(
            validator=validator.All(
                validator.Length(max=100),
                validator.Required(),
                karlvalidators.FolderNameAvailable(self.context),
                )
            )
        fields.insert(0, ('title', title_field))
        security_states = self._get_security_states()
        if security_states:
            fields.insert(4, ('security_state', security_field))
        return fields

    def form_widgets(self, fields):
        widgets = shared_widgets(self)
        widgets['tags'] = karlwidgets.TagsAddWidget()
        schema = dict(fields)
        if 'security_state' in schema:
            security_states = self._get_security_states()
            widgets['security_state'] = formish.RadioChoice(
                options=[ (s['name'], s['title']) for s in security_states],
                none_option=None)
        return widgets

    def __call__(self):
        api = TemplateAPI(self.context, self.request)
        return {'api':api, 'page_title':'Add Community'}

    def handle_cancel(self):
        return HTTPFound(location=model_url(self.context, self.request))

    def handle_submit(self, converted):
        request = self.request
        context = self.context
        name = make_name(context, converted['title'])
        userid = authenticated_userid(request)
        community = create_content(ICommunity,
                                   converted['title'],
                                   converted['description'],
                                   converted['text'],
                                   userid,
                                   )
        # this *must* directly follow content creation because the
        # toolinfo add stuff depends on the community having a full
        # path.
        context[name] = community

        # required to use moderators_group_name and
        # members_group_name
        community.__name__ = name
        for toolinfo in self.available_tools:
            if toolinfo['name'] in converted.get('tools', []):
                toolinfo['component'].add(community, request)

        # By default the "default tool" is None (indicating 'overview')
        community.default_tool = None

        users = find_users(context)
        moderators_group_name = community.moderators_group_name
        members_group_name = community.members_group_name

        for group_name in moderators_group_name, members_group_name:
            users.add_group(userid, group_name)

        if self.workflow is not None:
            if 'security_state' in converted:
                self.workflow.transition_to_state(community, request,
                                                  converted['security_state'])
        # Save the tags on it.
        set_tags(community, request, converted['tags'])
        # Adding a community should take you to the Add Existing
        # User screen, so the moderator can include some users.
        location = model_url(community, request,
                             'members', 'add_existing.html',
                             query={'status_message':'Community added'})
        return HTTPFound(location=location)

    def _get_security_states(self):
        return get_security_states(self.workflow, None, self.request)

def add_community(context, request): # b/c for start_over
    form = AddCommunityFormController(context, request)
    return form.handle_submit(request.POST)

class EditCommunityFormController(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.workflow = get_workflow(ICommunity, 'security', context)
        self.available_tools = get_available_tools(context, request)
        self.tools = [ (x['name'], x['title']) for x in self.available_tools ]
        selected_tools = []
        for info in self.available_tools:
            component = info['component']
            present = component.is_present(context, request)
            if present:
                selected_tools.append((info['name'], info['title']))
        self.selected_tools = selected_tools

    def form_defaults(self):
        context = self.context
        defaults = {
            'title':context.title,
            'tags': [], # initial values are supplied by widget
            'description':context.description,
            'text':context.text,
            'default_tool':getattr(context, 'default_tool', None),
            'tools':[t[0] for t in self.selected_tools],
            }
        if self.workflow is not None:
            defaults['security_state']  = self.workflow.state_of(context)
        return defaults

    def form_fields(self):
        fields = shared_fields()
        title_field = schemaish.String(
            validator=validator.All(
                validator.Length(max=100),
                validator.Required()))
        fields.insert(0, ('title', title_field))
        security_states = self._get_security_states()
        if security_states:
            fields.insert(4, ('security_state', security_field))
        fields.append(('default_tool', default_tool_field))
        return fields

    def form_widgets(self, fields):
        widgets = shared_widgets(self)
        tagdata = get_tags_client_data(self.context, self.request)
        widgets['tags'] = karlwidgets.TagsEditWidget(tagdata=tagdata)
        widgets['default_tool'] = formish.SelectChoice(
            options=self.selected_tools, none_option=('', 'Overview'))
        schema = dict(fields)
        if 'security_state' in schema:
            security_states = self._get_security_states()
            widgets['security_state'] = formish.RadioChoice(
                options=[ (s['name'], s['title']) for s in security_states],
                none_option=None)
        return widgets

    def __call__(self):
        api = TemplateAPI(self.context, self.request)
        return {'api':api, 'page_title':'Edit %s' % self.context.title,
                'actions':()}

    def handle_cancel(self):
        return HTTPFound(location=model_url(self.context, self.request))

    def handle_submit(self, converted):
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

    def _get_security_states(self):
        return get_security_states(self.workflow, self.context, self.request)

def get_recent_items_batch(community, request, size=10):
    batch = get_catalog_batch_grid(
        community, request, interfaces=[ICommunityContent],
        sort_index="modified_date", reverse=True, batch_size=size,
        path={'query': model_path(community)},
        allowed={'query': effective_principals(request), 'operator': 'or'},
    )
    return batch

def redirect_community_view(context, request):
    assert ICommunity.providedBy(context), str(type(context))

    default_tool = getattr(context, 'default_tool', None)
    if not default_tool:
        default_tool = 'view.html'
    return HTTPFound(location=model_url(context, request, default_tool))

def show_community_view(context, request):
    assert ICommunity.providedBy(context), str(type(context))

    user = authenticated_userid(request)
    page_title = 'View Community ' + context.title
    api = TemplateAPI(context, request, page_title)

    # provide client data for rendering current tags in the tagbox
    tagquery = getMultiAdapter((context, request), ITagQuery)
    client_json_data = dict(
        tagbox = dict(
            docid = tagquery.docid,
            records = tagquery.tagswithcounts,
            ),
        )

    # Filter the actions based on permission
    actions = []
    if has_permission('moderate', context, request):
        actions.append(('Edit', 'edit.html'))

    # If user has permission to see this view then has permission to join.
    if not(user in context.member_names or user in context.moderator_names):
        actions.append(('Join', 'join.html'))

    if has_permission('moderate', context, request):
        actions.append(('Delete', 'delete.html'))

    recent_items = []
    recent_items_batch = get_recent_items_batch(context, request)
    for item in recent_items_batch["entries"]:
        adapted = getMultiAdapter((item, request), IGridEntryInfo)
        recent_items.append(adapted)

    feed_url = model_url(context, request, "atom.xml")
    return render_template_to_response(
        'templates/community.pt',
        api=api,
        actions=actions,
        recent_items=recent_items,
        batch_info=recent_items_batch,
        head_data=convert_to_script(client_json_data),
        feed_url=feed_url,
    )

def join_community_view(context, request):
    """ User sends an email to community moderator(s) asking to join
    the community.  Email contains a link to "add_existing" view, in members,
    that a moderator can use to add member to the community.

    """
    assert ICommunity.providedBy(context)

    # Get logged in user
    profiles = find_profiles(context)
    user = authenticated_userid(request)
    profile = profiles[user]

    # Handle form submission
    if "form.submitted" in request.POST:
        message = request.POST.get("message", "")
        moderators = [profiles[id] for id in context.moderator_names]
        mail = karl.mail.Message()
        mail["From"] = "%s <%s>" % (profile.title, profile.email)
        mail["To"] = ",".join(
            ["%s <%s>" % (p.title, p.email) for p in moderators]
        )
        mail["Subject"] = "Request to join %s community" % context.title

        body_template = get_template("templates/email_join_community.pt")
        profile_url = model_url(profile, request)
        accept_url=model_url(context, request, "members", "add_existing.html",
                             query={"user_id": user})
        body = body_template(
            message=message,
            community_title=context.title,
            person_name=profile.title,
            profile_url=profile_url,
            accept_url=accept_url
        )

        if isinstance(body, unicode):
            body = body.encode("UTF-8")

        mail.set_payload(body, "UTF-8")
        mail.set_type("text/html")

        recipients = [p.email for p in moderators]
        mailer = getUtility(IMailDelivery)
        mailer.send(profile.email, recipients, mail)

        status_message = "Your request has been sent to the moderators."
        location = model_url(context, request,
                             query={"status_message": status_message})

        return HTTPFound(location=location)

    # Show form
    page_title = "Join " + context.title
    api = TemplateAPI(context, request, page_title)
    return render_template_to_response(
        "templates/join_community.pt",
        api=api,
        profile=profile,
        community=context,
        post_url=model_url(context, request, "join.html"),
        formfields=api.formfields,
    )

def delete_community_view(context, request):

    page_title = 'Delete ' + context.title
    api = TemplateAPI(context, request, page_title)

    confirm = request.params.get('confirm', False)
    if confirm == '1':
        name = context.__name__
        del context.__parent__[name]
        location = model_url(context.__parent__, request)
        return HTTPFound(location=location)

    # Get a layout
    layout_provider = get_layout_provider(context, request)
    layout = layout_provider('community')

    return render_template_to_response(
        'templates/delete_resource.pt',
        api=api,
        layout=layout,
        num_children=0,
        )

class CommunitySidebar(object):
    implements(ISidebar)

    def __init__(self, context, request):
        pass

    def __call__(self, api):
        return render_template(
            'templates/community_sidebar.pt',
            api=api)
