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

import urllib

from webob.exc import HTTPFound
from zope.component.event import objectEventNotify

from zope.component import getMultiAdapter
from zope.component import queryUtility

from repoze.enformed import FormSchema
from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.security import authenticated_userid
from repoze.bfg.security import has_permission
from repoze.bfg.url import model_url
from repoze.workflow import get_workflow

from karl.events import ObjectModifiedEvent
from karl.events import ObjectWillBeModifiedEvent
from karl.views.api import TemplateAPI
from karl.utilities.alerts import Alerts
from karl.utilities.interfaces import IAlerts

from karl.utils import find_interface
from karl.utils import support_attachments

from repoze.lemonade.content import create_content
from karl.models.interfaces import IComment
from karl.content.interfaces import IBlogEntry
from karl.content.interfaces import IForumTopic
from karl.content.views.utils import extract_description
from karl.content.views.interfaces import IBylineInfo
from karl.views.interfaces import ILayoutProvider
from karl.views.form import render_form_to_response
from karl.views.baseforms import security_state as security_state_field
from karl.content.views.utils import fetch_attachments
from karl.content.views.utils import store_attachments

from karl.security.workflow import get_security_states
from karl.views import baseforms
from formencode import Invalid

class AddCommentForm(FormSchema):
    add_comment = baseforms.add_comment
    sendalert = baseforms.sendalert

EditCommentForm = AddCommentForm

def redirect_comments_view(context, request):
    # When deleting a comment, we get redirected to the parent.  It's
    # easier to implement another redirect than re-implement the
    # delete view.

    url = model_url(context.__parent__, request)
    status_message = request.GET.get('status_message', False)
    if status_message:
        msg = '?status_message=' + status_message
    else:
        msg = ''
    return HTTPFound(location=url+msg)

def show_comment_view(context, request):

    page_title = "Comment on " + context.title
    api = TemplateAPI(context, request, page_title)

    actions = []
    if has_permission('edit', context, request):
        actions.append(('Edit', 'edit.html'))
    if has_permission('delete', context, request):
        actions.append(('Delete', 'delete.html'))

    byline_info = getMultiAdapter((context, request), IBylineInfo)
    container = find_interface(context, IBlogEntry)
    if container is None:
        # Comments can also be in forum topics
        container = find_interface(context, IForumTopic)
    backto = {
        'href': model_url(container, request),
        'title': container.title,
        }

    # Get a layout
    layout_provider = getMultiAdapter((context, request), ILayoutProvider)
    layout = layout_provider('community')

    if support_attachments(context):
        attachments = fetch_attachments(context, request)
    else:
        attachments = ()

    return render_template_to_response(
        'templates/show_comment.pt',
        api=api,
        actions=actions,
        byline_info=byline_info,
        attachments=attachments,
        backto=backto,
        layout=layout,
        )

def add_comment_view(context, request):
    # This is NOT a self-posting form.  The BlogEntry has the form
    # that submits to this view.  Thus, we only need to handle
    # submission requests, then redirect back to the parent (the blog
    # entry).

    # Handle the Add Comment form
    #post_url = model_url(context, request, "comments/add_comment.html")
    form = AddCommentForm()
    # add the security state field if appropriate for the context
    workflow = get_workflow(IComment, 'security', context)

    if workflow is None:
        security_states = []
    else:
        security_states = get_security_states(workflow, None, request)

    if security_states:
        form.add_field('security_state', security_state_field)

    if 'form.cancel' in request.POST:
        return HTTPFound(location=model_url(context.__parent__, request))

    if 'form.submitted' in request.POST:
        converted = form.validate(request.POST)
        form.is_valid = True
        parent = context.__parent__
        creator = authenticated_userid(request)
        c = create_content(
            IComment,
            'Re: %s' % parent.title,
            converted['add_comment'],
            extract_description(converted['add_comment']),
            creator,
            )
        next_id = parent['comments'].next_id
        parent['comments'][next_id] = c
        if workflow is not None:
            workflow.initialize(c)
            if 'security_state' in converted:
                workflow.transition_to_state(c, request,
                                             converted['security_state'])

        if support_attachments(c):
            store_attachments(c, request.params, creator)

        url = model_url(parent, request)
        msg = 'Comment added'
        url = url + '?status_message=%s' % urllib.quote(msg)

        blogentry = find_interface(context, IBlogEntry)
        if converted['sendalert']:
            alerts = queryUtility(IAlerts, default=Alerts())
            alerts.emit(c, request)

        return HTTPFound(location=url)

    # XXX Need different flow of control here, since it isn't
    # self-posting.

    else:
        raise Invalid('This is not a self-posting form. It is submit only.',
                      None, None)

def edit_comment_view(context, request):

    form = EditCommentForm()
    workflow = get_workflow(IComment, 'security', context)

    if workflow is None:
        security_states = []
    else:
        security_states = get_security_states(workflow, context, request)

    if security_states:
        form.add_field('security_state', security_state_field)

    if 'form.cancel' in request.POST:
        return HTTPFound(location=model_url(context.__parent__, request))

    if 'form.submitted' in request.POST:
        try:
            converted = form.validate(request.POST)
            form.is_valid = True

            # *will be* modified event
            objectEventNotify(ObjectWillBeModifiedEvent(context))
            if workflow is not None:
                if 'security_state' in converted:
                    workflow.transition_to_state(context, request,
                                                 converted['security_state'])

            context.text  = converted['add_comment']
            context.description = extract_description(context.text)

            creator = authenticated_userid(request)
            if support_attachments(context):
                store_attachments(context, request.params, creator)

            context.modified_by = authenticated_userid(request)
            objectEventNotify(ObjectModifiedEvent(context))

            location = model_url(context, request)
            return HTTPFound(location=location)

        except Invalid, e:
            fielderrors = e.error_dict
            fill_values = form.convert(request.POST)
    else:
        fielderrors = {}
        state = baseforms.AppState()
        if workflow is None:
            security_state = ''
        else:
            security_state = workflow.state_of(context)
        fill_values = dict(
            add_comment=context.text,
            security_state = security_state)

    # Render the form and shove some default values in
    page_title = 'Edit ' + context.title
    api = TemplateAPI(context, request, page_title)

    # Get a layout
    layout_provider = getMultiAdapter((context, request), ILayoutProvider)
    layout = layout_provider('community')

    if support_attachments(context):
        attachments = fetch_attachments(context, request)
    else:
        attachments = ()

    return render_form_to_response(
        'templates/edit_comment.pt',
        form,
        fill_values,
        post_url=request.url,
        formfields=api.formfields,
        fielderrors=fielderrors,
        api=api,
        attachments=attachments,
        layout=layout,
        security_states = security_states,
        )
