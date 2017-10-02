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

import schemaish
import formish
from validatish import validator

from repoze.lemonade.content import create_content
from repoze.postoffice.message import Message

from zope.component.event import objectEventNotify
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component import getUtility
from zope.interface import implements
from pyramid.httpexceptions import HTTPFound

from pyramid.renderers import get_renderer
from pyramid.renderers import render
from pyramid.security import authenticated_userid
from pyramid.security import effective_principals
from pyramid.security import has_permission
from pyramid.traversal import resource_path
from pyramid.url import resource_url

from repoze.sendmail.interfaces import IMailDelivery

from karl.events import ObjectWillBeModifiedEvent
from karl.events import ObjectModifiedEvent

from karl.models.interfaces import ICatalogSearch
from karl.models.interfaces import ISQLCatalogSearch
from karl.models.interfaces import ICommunity
from karl.models.interfaces import ICommunityContent
from karl.models.interfaces import IGridEntryInfo
from karl.models.interfaces import IProfile
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

from karl.security.policy import ADMINISTER
from karl.security.policy import DELETE_COMMUNITY
from karl.security.policy import MODERATE
from karl.security.workflow import get_security_states

def get_recent_items_batch(community, request, size=10):
    batch = get_catalog_batch_grid(
        community, request, interfaces=[ICommunityContent],
        sort_index="modified_date", reverse=True, batch_size=size,
        community=community,
        can_view={'query': effective_principals(request), 'operator': 'or'},
        catalog_iface=ISQLCatalogSearch,
    )
    return batch

def redirect_community_view(context, request):
    assert ICommunity.providedBy(context), str(type(context))

    default_tool = getattr(context, 'default_tool', None)
    if not default_tool:
        default_tool = 'view.html'
    # Preserve status_message=, etc in query string
    query = request.GET
    if query:
        location = resource_url(context, request, default_tool, query=query)
    else:
        location = resource_url(context, request, default_tool)
    return HTTPFound(location=location)

def show_community_view(context, request):
    assert ICommunity.providedBy(context), str(type(context))

    user = authenticated_userid(request)
    page_title = 'View Community ' + context.title
    api = TemplateAPI(context, request, page_title)

    # provide client data for rendering current tags in the tagbox
    tagquery = getMultiAdapter((context, request), ITagQuery)
    client_json_data = {'tagbox': {'docid': tagquery.docid,
                                   'records': tagquery.tagswithcounts,
                                  },
                       }

    # Filter the actions based on permission
    actions = []
    if has_permission(MODERATE, context, request):
        actions.append(('Edit', 'edit.html'))

    # If user has permission to see this view then has permission to join.
    if not(user in context.member_names or user in context.moderator_names):
        actions.append(('Join', 'join.html'))

    if has_permission(DELETE_COMMUNITY, context, request):
        actions.append(('Delete', 'delete.html'))

    if has_permission(ADMINISTER, context, request):
        actions.append(('Advanced', 'advanced.html'))

    recent_items = []
    recent_items_batch = get_recent_items_batch(context, request)
    for item in recent_items_batch["entries"]:
        adapted = getMultiAdapter((item, request), IGridEntryInfo)
        if adapted is not None:
            recent_items.append(adapted)

    feed_url = resource_url(context, request, "atom.xml")

    return {'api': api,
            'actions': actions,
            'recent_items': recent_items,
            'batch_info': recent_items_batch,
            'head_data': convert_to_script(client_json_data),
            'feed_url': feed_url
           }

def community_recent_items_ajax_view(context, request):
    assert ICommunity.providedBy(context), str(type(context))

    recent_items = []
    recent_items_batch = get_recent_items_batch(context, request, 5)
    for item in recent_items_batch["entries"]:
        adapted = getMultiAdapter((item, request), IGridEntryInfo)
        recent_items.append(adapted)

    return {'items': recent_items}

def get_members_batch(community, request, size=10):
    mods = list(community.moderator_names)
    any = list(community.member_names | community.moderator_names)
    principals = effective_principals(request)
    searcher = ICatalogSearch(community)
    total, docids, resolver = searcher(interfaces=[IProfile],
                                       limit=size,
                                       name={'query': any,
                                             'operator': 'or'},
                                       allowed={'query': principals,
                                                'operator': 'or'},
                                      )
    mod_entries = []
    other_entries = []

    for docid in docids:
        model = resolver(docid)
        if model is not None:
            if model.__name__ in mods:
                mod_entries.append(model)
            else:
                other_entries.append(model)

    return (mod_entries + other_entries)[:size]


def community_members_ajax_view(context, request):
    assert ICommunity.providedBy(context), str(type(context))

    members = []
    members_batch = get_members_batch(context, request, 5)
    for item in members_batch:
        adapted = getMultiAdapter((item, request), IGridEntryInfo)
        adapted.moderator = item.__name__ in context.moderator_names
        members.append(adapted)

    return {'items': members}


def related_communities_ajax_view(context, request):
    assert ICommunity.providedBy(context), str(type(context))

    related = []
    principals = effective_principals(request)
    searcher = ICatalogSearch(context)
    search = ' OR '.join(context.title.lower().split())
    total, docids, resolver = searcher(interfaces=[ICommunity],
                                       limit=5,
                                       reverse=True,
                                       sort_index="modified_date",
                                       texts=search,
                                       allowed={'query': principals,
                                                'operator': 'or'},
                                      )
    for docid in docids:
        model = resolver(docid)
        if model is not None:
            if model is not context:
                adapted = getMultiAdapter((model, request), IGridEntryInfo)
                related.append(adapted)

    return {'items': related}


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

sendalert_default_field = schemaish.Boolean(
    description=('Send alerts by default on content creation?'))

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
        'sendalert_default': True,
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
        fields.append(('default_tool', default_tool_field))
        fields.append(('sendalert_default', sendalert_default_field))
        return fields

    def form_widgets(self, fields):
        widgets = shared_widgets(self)
        widgets['tags'] = karlwidgets.TagsAddWidget()
        widgets['default_tool'] = formish.SelectChoice(
            options=self.tools, none_option=('', 'Overview'))
        widgets['sendalert_default'] = formish.Checkbox()
        schema = dict(fields)
        if 'security_state' in schema:
            security_states = self._get_security_states()
            widgets['security_state'] = formish.RadioChoice(
                options=[ (s['name'], s['title']) for s in security_states],
                none_option=None)
        return widgets

    def __call__(self):
        api = TemplateAPI(self.context, self.request, 'Add Community')
        return {'api':api}

    def handle_cancel(self):
        return HTTPFound(location=resource_url(self.context, self.request))

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
        community.sendalert_default = converted.get('sendalert_default', True)
        # this *must* directly follow content creation because the
        # toolinfo add stuff depends on the community having a full
        # path.
        context[name] = community

        # required to use moderators_group_name and
        # members_group_name
        community.__name__ = name
        tools_present = []
        for toolinfo in self.available_tools:
            if toolinfo['name'] in converted.get('tools', []):
                toolinfo['component'].add(community, request)
                tools_present.append(toolinfo['name'])

        # Set the default tool
        if converted.get('default_tool') in tools_present:
            community.default_tool = converted['default_tool']
        else:
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
        location = resource_url(community, request,
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
            'sendalert_default':getattr(context, 'sendalert_default', True),
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
        fields.append(('sendalert_default', sendalert_default_field))
        return fields

    def form_widgets(self, fields):
        widgets = shared_widgets(self)
        tagdata = get_tags_client_data(self.context, self.request)
        widgets['tags'] = karlwidgets.TagsEditWidget(tagdata=tagdata)
        widgets['default_tool'] = formish.SelectChoice(
            options=self.selected_tools, none_option=('', 'Overview'))
        widgets['sendalert_default'] = formish.Checkbox()
        schema = dict(fields)
        if 'security_state' in schema:
            security_states = self._get_security_states()
            widgets['security_state'] = formish.RadioChoice(
                options=[ (s['name'], s['title']) for s in security_states],
                none_option=None)
        return widgets

    def __call__(self):
        page_title = 'Edit %s' % self.context.title
        api = TemplateAPI(self.context, self.request, page_title)
        return {'api':api, 'actions':()}

    def handle_cancel(self):
        return HTTPFound(location=resource_url(self.context, self.request))

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
        context.modified_by = authenticated_userid(request)
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
        context.sendalert_default = converted['sendalert_default']

        # *modified* event
        objectEventNotify(ObjectModifiedEvent(context))
        location = resource_url(context, request)
        return HTTPFound(location=location)

    def _get_security_states(self):
        return get_security_states(self.workflow, self.context, self.request)

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
        mail = Message()
        mail["From"] = "%s <%s>" % (profile.title, profile.email)
        mail["To"] = ",".join(
            ["%s <%s>" % (p.title, p.email) for p in moderators]
        )
        mail["Subject"] = "Request to join %s community" % context.title

        body_template = get_renderer(
            "templates/email_join_community.pt").implementation()
        profile_url = resource_url(profile, request)
        accept_url=resource_url(context, request, "members", "add_existing.html",
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
        mailer.send(recipients, mail)

        status_message = "Your request has been sent to the moderators."
        location = resource_url(context, request,
                             query={"status_message": status_message})

        return HTTPFound(location=location)

    # Show form
    page_title = "Join " + context.title
    api = TemplateAPI(context, request, page_title)
    return dict(api=api,
             profile=profile,
             community=context,
             post_url=resource_url(context, request, "join.html"),
             formfields=api.formfields)

def delete_community_view(context, request):

    page_title = 'Delete ' + context.title
    api = TemplateAPI(context, request, page_title)

    confirm = request.params.get('confirm', False)
    if confirm == '1':
        name = context.__name__
        del context.__parent__[name]
        location = resource_url(context.__parent__, request)
        return HTTPFound(location=location)

    # Get a layout
    layout_provider = get_layout_provider(context, request)
    layout = layout_provider('community')

    return dict(api=api,
             layout=layout,
             num_children=0,)

class CommunitySidebar(object):
    implements(ISidebar)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, api):
        return render(
            'templates/community_sidebar.pt',
            dict(api=api),
            request=self.request
            )
