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
from webob.exc import HTTPExpectationFailed
from zope.component.event import objectEventNotify

from zope.component import getMultiAdapter
from zope.component import queryUtility

from schemaish.type import File as SchemaFile
import schemaish

from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.security import authenticated_userid
from repoze.bfg.security import has_permission
from repoze.bfg.url import model_url
from repoze.workflow import get_workflow

from karl.events import ObjectModifiedEvent
from karl.events import ObjectWillBeModifiedEvent
from karl.views.api import TemplateAPI
from karl.utilities.alerts import Alerts
from karl.utilities.image import relocate_temp_images
from karl.utilities.interfaces import IAlerts

from karl.utils import get_layout_provider
from karl.utils import find_interface
from karl.utils import support_attachments

from repoze.lemonade.content import create_content
from karl.models.interfaces import IComment
from karl.content.interfaces import IBlogEntry
from karl.content.interfaces import IForumTopic
from karl.content.views.utils import extract_description
from karl.content.views.utils import get_show_sendalert
from karl.content.views.utils import upload_attachments
from karl.content.views.interfaces import IBylineInfo
from karl.views.forms.filestore import get_filestore
from karl.views.forms import widgets as karlwidgets
from karl.content.views.utils import fetch_attachments


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
    # avoid Unicode errors on webob.multidict or webob.descriptors.
    # only way to keep both happy from our end, since the redirect
    # complicates things
    location = url+msg
    location = location.encode('utf-8')
    return HTTPFound(location=location)

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
    layout_provider = get_layout_provider(context, request)
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

add_comment_field = schemaish.String(
    title='Add Comment',
    description='Enter your comments below.')
sendalert_field = schemaish.Boolean(
    title='Send email alert to community members?')
attachments_field = schemaish.Sequence(schemaish.File(),
    title='Attachments',
    )

class AddCommentFormController(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.filestore = get_filestore(context, request, 'comment')
        self.show_sendalert = get_show_sendalert(context, request)

    def form_defaults(self):
        if self.show_sendalert:
            return {'sendalert': True}
        return {}

    def form_fields(self):
        fields = [('add_comment', add_comment_field),
                  ('attachments', attachments_field),
                  ]
        if self.show_sendalert:
            fields.append(('sendalert', sendalert_field))
        return fields

    def form_widgets(self, fields):
        widgets = {
            'add_comment': karlwidgets.RichTextWidget(empty=''),
            'attachments': karlwidgets.AttachmentsSequence(sortable=False,
                                                           min_start_fields=0),
            'attachments.*': karlwidgets.FileUpload2(filestore=self.filestore),
            }
        if self.show_sendalert:
            widgets['sendalert'] = karlwidgets.SendAlertCheckbox()
        return widgets

    def __call__(self):
        raise HTTPExpectationFailed(u'This is not a self-posting form. '
                                     u'It is submit only.')

    def handle_cancel(self):
        location = model_url(self.context.__parent__, self.request)
        return HTTPFound(location=location)

    def handle_submit(self, converted):
        context = self.context
        request = self.request
        parent = context.__parent__
        creator = authenticated_userid(request)
        comment = create_content(
            IComment,
            'Re: %s' % parent.title,
            converted['add_comment'],
            extract_description(converted['add_comment']),
            creator,
            )
        next_id = parent['comments'].next_id
        parent['comments'][next_id] = comment
        workflow = get_workflow(IComment, 'security', context)
        if workflow is not None:
            workflow.initialize(comment)
            if 'security_state' in converted:
                workflow.transition_to_state(comment, request,
                                             converted['security_state'])

        if support_attachments(comment):
            upload_attachments(converted['attachments'], comment,
                               creator, request)
        relocate_temp_images(comment, request)

        blogentry = find_interface(context, IBlogEntry)
        if converted.get('sendalert'):
            alerts = queryUtility(IAlerts, default=Alerts())
            alerts.emit(comment, request)

        location = model_url(parent, request)
        msg = 'Comment added'
        location = '%s?status_message=%s' % (location, urllib.quote(msg))
        self.filestore.clear()
        return HTTPFound(location=location)

class EditCommentFormController(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.filestore = get_filestore(context, request, 'comment')

    def form_fields(self):
        fields = [('add_comment', add_comment_field),
                  ('attachments', attachments_field),
                  ]
        return fields

    def form_widgets(self, fields):
        widgets = {
            'add_comment': karlwidgets.RichTextWidget(empty=''),
            'attachments': karlwidgets.AttachmentsSequence(sortable=False,
                                                           min_start_fields=0),
            'attachments.*': karlwidgets.FileUpload2(filestore=self.filestore),
            }
        return widgets

    def form_defaults(self):
        context = self.context
        attachments = [SchemaFile(None, x.__name__, x.mimetype)
                       for x in context.values()]
        defaults = {'add_comment': context.text,
                    'attachments': attachments,
                    }
        return defaults

    def __call__(self):
        context = self.context
        request = self.request
        page_title = 'Edit %s' % context.title
        api = TemplateAPI(context, self.request, page_title)
        # Get a layout
        layout_provider = get_layout_provider(context, request)
        layout = layout_provider('community')
        return {'api': api, 'actions': (), 'layout': layout}

    def handle_cancel(self):
        context = self.context
        blogentry = find_interface(self.context, IBlogEntry)
        return HTTPFound(location=model_url(blogentry, self.request))

    def handle_submit(self, converted):
        context = self.context
        request = self.request
        workflow =  get_workflow(IComment, 'security', context)

        objectEventNotify(ObjectWillBeModifiedEvent(context))
        if workflow is not None:
            if 'security_state' in converted:
                workflow.transition_to_state(context, request,
                                             converted['security_state'])
        context.text = converted['add_comment']
        context.description = extract_description(context.text)
        creator = authenticated_userid(request)
        if support_attachments(context):
            upload_attachments(converted['attachments'], context, creator,
                               request)
        context.modified_by = creator
        objectEventNotify(ObjectModifiedEvent(context))
        location = model_url(context, request)
        self.filestore.clear()
        return HTTPFound(location=location)
