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

from webob.exc import HTTPFound

from zope.component.event import objectEventNotify

from schemaish.type import File as SchemaFile
from validatish import validator
import formish
import schemaish

from repoze.bfg.chameleon_zpt import render_template_to_response

from repoze.bfg.url import model_url
from repoze.bfg.security import authenticated_userid
from repoze.bfg.security import has_permission

from repoze.lemonade.content import create_content

from karl.content.interfaces import IPage

from karl.events import ObjectModifiedEvent
from karl.events import ObjectWillBeModifiedEvent
from karl.utils import find_community

from karl.views.api import TemplateAPI

from karl.views.forms import validators as karlvalidators
from karl.views.forms import widgets as karlwidgets
from karl.views.forms.filestore import get_filestore
from karl.views.utils import convert_to_script
from karl.views.utils import make_unique_name
from karl.views.tags import set_tags
from karl.views.tags import get_tags_client_data

from karl.content.views.utils import extract_description
from karl.content.views.utils import get_previous_next
from karl.content.views.utils import fetch_attachments
from karl.content.views.utils import upload_attachments

from karl.utils import get_layout_provider

tags_field = schemaish.Sequence(schemaish.String())
text_field = schemaish.String()
attachments_field = schemaish.Sequence(
    schemaish.File(),
    title='Attachments',
    description='You can remove an attachment by clicking the checkbox. '
    'Removal will come to effect after saving the page and can be '
    'reverted by cancel.')

class AddPageFormController(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.filestore = get_filestore(context, request, 'page')

    def form_defaults(self):
        defaults = {
            'title': '',
            'tags': [],
            'text': '',
            'attachments': [],
            }
        return defaults

    def form_fields(self):
        title_field = schemaish.String(
            validator=validator.All(
                validator.Length(max=100),
                validator.Required(),
                karlvalidators.FolderNameAvailable(self.context),
                )
            )
        fields = [('title', title_field),
                  ('tags', tags_field),
                  ('text', text_field),
                  ('attachments', attachments_field),
                  ]
        return fields

    def form_widgets(self, fields):
        widgets = {
            'title': formish.Input(empty=''),
            'tags': karlwidgets.TagsAddWidget(),
            'text': karlwidgets.RichTextWidget(empty=''),
            'attachments': formish.widgets.SequenceDefault(sortable=False),
            'attachments.*': karlwidgets.FileUpload2(filestore=self.filestore),
            }
        return widgets

    def __call__(self):
        context = self.context
        request = self.request
        api = TemplateAPI(context, request, 'Add Page')
        community = find_community(context)
        layout_provider = get_layout_provider(context, request)
        if community is not None:
            layout = layout_provider('community')
        else:
            layout = layout_provider('generic')
        return {'api': api, 'actions': (), 'layout': layout}

    def handle_cancel(self):
        return HTTPFound(location=model_url(self.context, self.request))

    def handle_submit(self, converted):
        context = self.context
        request = self.request
        # create the page and store it
        creator = authenticated_userid(request)
        page = create_content(IPage,
                              converted['title'],
                              converted['text'],
                              extract_description(converted['text']),
                              creator,
                              )
        name = make_unique_name(context, converted['title'])
        context[name] = page

        # tags and attachments
        set_tags(page, request, converted['tags'])
        attachments_folder = page['attachments']
        upload_attachments(converted['attachments'], attachments_folder,
                           creator, request)

        # update ordering if in ordered container
        if hasattr(context, 'ordering'):
            context.ordering.add(name)

        location = model_url(page, request)
        self.filestore.clear()
        return HTTPFound(location=location)

class EditPageFormController(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.filestore  = get_filestore(context, request, 'page')


    def form_defaults(self):
        context = self.context
        attachments = [SchemaFile(None, x.__name__, x.mimetype)
                       for x in context['attachments'].values()]
        defaults = {
            'title': context.title,
            'tags': [], # initial values supplied by widget
            'text': context.text,
            'attachments': attachments,
            }
        return defaults

    def form_fields(self):
        title_field = schemaish.String(
            validator=validator.All(
                validator.Length(max=100),
                validator.Required(),
                )
            )
        fields = [('title', title_field),
                  ('tags', tags_field),
                  ('text', text_field),
                  ('attachments', attachments_field),
                  ]
        return fields

    def form_widgets(self, fields):
        tagdata = get_tags_client_data(self.context, self.request)
        widgets = {
            'title': formish.Input(empty=''),
            'tags': karlwidgets.TagsEditWidget(tagdata=tagdata),
            'text': karlwidgets.RichTextWidget(empty=''),
            'attachments': formish.widgets.SequenceDefault(sortable=False),
            'attachments.*': karlwidgets.FileUpload2(filestore=self.filestore),
            }
        return widgets

    def __call__(self):
        context = self.context
        request = self.request
        page_title = 'Edit %s' % context.title
        api = TemplateAPI(context, request, page_title)
        community = find_community(context)
        layout_provider = get_layout_provider(context, request)
        if community is not None:
            layout = layout_provider('community')
        else:
            layout = layout_provider('generic')
        return {'api': api, 'actions': (), 'layout': layout}

    def handle_cancel(self):
        return HTTPFound(location=model_url(self.context, self.request))

    def handle_submit(self, converted):
        context = self.context
        request = self.request
        userid = authenticated_userid(request)
        # *will be* modified event
        objectEventNotify(ObjectWillBeModifiedEvent(context))

        context.title = converted['title']
        context.text = converted['text']
        context.description = extract_description(converted['text'])

        # tags and attachments
        set_tags(context, request, converted['tags'])
        creator = userid
        attachments_folder = context['attachments']
        upload_attachments(converted['attachments'], attachments_folder,
                           creator, request)

        # modified
        context.modified_by = userid
        objectEventNotify(ObjectModifiedEvent(context))

        self.filestore.clear()
        location = model_url(context, request)
        msg = "?status_message=Page%20edited"
        return HTTPFound(location=location+msg)

def show_page_view(context, request):

    backto = {
        'href': model_url(context.__parent__, request),
        'title': context.__parent__.title,
        }

    actions = []
    if has_permission('create', context, request):
        actions.append(
            ('Edit', 'edit.html')
            )
    if has_permission('delete', context, request):
        actions.append(
            ('Delete', 'delete.html'),
        )

    page_title = context.title
    api = TemplateAPI(context, request, page_title)

    previous, next = get_previous_next(context, request)

    # provide client data for rendering current tags in the tagbox
    client_json_data = dict(
        tagbox = get_tags_client_data(context, request),
        )

    # Get a layout
    community = find_community(context)
    layout_provider = get_layout_provider(context, request)
    if community is not None:
        layout = layout_provider('community')
    else:
        layout = layout_provider('generic')

    return render_template_to_response(
        'templates/show_page.pt',
        api=api,
        actions=actions,
        attachments=fetch_attachments(context['attachments'], request),
        formfields=api.formfields,
        head_data=convert_to_script(client_json_data),
        backto=backto,
        previous=previous,
        next=next,
        layout=layout,
        )
