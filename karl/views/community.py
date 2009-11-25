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

import email.message

from zope.component.event import objectEventNotify
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
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
from repoze.enformed import FormSchema

from repoze.sendmail.interfaces import IMailDelivery

from formencode import validators
from formencode import Invalid

from karl.events import ObjectWillBeModifiedEvent
from karl.events import ObjectModifiedEvent

from karl.models.interfaces import ICommunity
from karl.models.interfaces import ICommunityContent
from karl.models.interfaces import IGridEntryInfo
from karl.models.interfaces import ITagQuery

from repoze.workflow import get_workflow

from karl.utils import get_layout_provider
from karl.utils import find_profiles
from karl.utils import get_setting

from karl.views.adapters import DefaultToolAddables
from karl.views.api import TemplateAPI
from karl.views.interfaces import ISidebar
from karl.views.interfaces import IToolAddables
from karl.views.utils import convert_to_script
from karl.views.batch import get_catalog_batch_grid
from karl.views import baseforms
from karl.views.tags import set_tags
from karl.views.form import render_form_to_response
from karl.security.workflow import get_security_states
from karl.views.baseforms import security_state as security_state_field

class EditCommunityForm(FormSchema):
    title = baseforms.title
    tags = baseforms.tags
    description = baseforms.description
    text = validators.UnicodeString(strip=True)

def edit_community_view(context, request):
    if 'form.cancel' in request.POST:
        return HTTPFound(location=model_url(context, request))

    system_name = get_setting(context, 'system_name', 'KARL')
    workflow = get_workflow(ICommunity, 'security', context)
    available_tools = queryMultiAdapter(
        (context, request), IToolAddables,
        default=DefaultToolAddables(context, request))()

    tags_list = request.POST.getall('tags')
    form = EditCommunityForm(tags_list=tags_list)

    if workflow is None:
        security_states = []
    else:
        security_states = get_security_states(workflow, context, request)

    if security_states:
        form.add_field('security_state', security_state_field)

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
                s = request.params.has_key(info['name'])
                tools.append(
                    {'name': info['name'], 'title': info['title'],
                     'state': s}
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
        'templates/edit_community.pt',
        form,
        fill_values,
        post_url=request.url,
        formfields = api.formfields,
        fielderrors = fielderrors,
        tools = tools,
        default_tools = default_tools,
        api = api,
        system_name = system_name,
        head_data = convert_to_script(client_json_data),
        security_states = security_states,
        )

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
        mail = email.message.Message()
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
        mailer.send(profile.email, recipients, mail.as_string())

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
