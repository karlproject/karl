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

import formish
import schemaish
from schemaish.type import File as SchemaFile
from validatish import validator

from repoze.bfg.chameleon_zpt import render_template_to_response

from repoze.bfg.url import model_url
from repoze.bfg.security import authenticated_userid
from repoze.bfg.security import has_permission

from repoze.lemonade.content import create_content

from karl.content.interfaces import INewsItem
from karl.content.views.utils import upload_attachments

from karl.events import ObjectModifiedEvent
from karl.events import ObjectWillBeModifiedEvent

from karl.views.api import TemplateAPI

from karl.views.forms import attr as karlattr
from karl.views.forms import validators as karlvalidators
from karl.views.forms import widgets as karlwidgets
from karl.views.forms.filestore import get_filestore
from karl.views.tags import set_tags
from karl.views.tags import get_tags_client_data
from karl.views.utils import convert_to_script
from karl.views.utils import handle_photo_upload
from karl.views.utils import make_unique_name
from karl.views.utils import photo_from_filestore_view

from karl.content.views.utils import get_previous_next
from karl.content.views.utils import fetch_attachments

from karl.utils import get_layout_provider

import datetime

_NOW = None

def _now():
    if _NOW is not None:
        return _NOW
    return datetime.datetime.now()

tags_field = schemaish.Sequence(schemaish.String())
text_field = schemaish.String()
attachments_field = schemaish.Sequence(schemaish.File(), title='Attachments')
photo_field = schemaish.File()
caption_field = schemaish.String()
publication_date_field = karlattr.KarlDateTime(validator=validator.Required())

class AddNewsItemFormController(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.filestore = get_filestore(context, request, 'newsitem')
        page_title = getattr(self, 'page_title', 'Add News Item')
        self.api = TemplateAPI(context, request, page_title)

    def form_defaults(self):
        now = _now()
        defaults = {
            'title': '',
            'tags': [],
            'text': '',
            'attachments': None,
            'photo': None,
            'caption': '',
            'publication_date': now}
        return defaults

    def form_fields(self):
        title_field = schemaish.String(
            validator=validator.All(
                validator.Length(max=100),
                validator.Required(),
                karlvalidators.FolderNameAvailable(self.context)))
        fields = [('title', title_field),
                  ('tags', tags_field),
                  ('text', text_field),
                  ('attachments', attachments_field),
                  ('photo', photo_field),
                  ('caption', caption_field),
                  ('publication_date', publication_date_field),
                  ]
        return fields

    def form_widgets(self, fields):
        default_icon = '%s/images/image.png' % self.api.static_url
        widgets = {'title': formish.Input(empty=''),
                   'tags': karlwidgets.TagsAddWidget(),
                   'text': karlwidgets.RichTextWidget(empty=''),
                   'attachments': formish.SequenceDefault(sortable=False),
                   'attachments.*': karlwidgets.FileUpload2(
                       filestore=self.filestore),
                   'photo': karlwidgets.PhotoImageWidget(
                       filestore=self.filestore,
                       url_base=model_url(self.context, self.request),
                       show_image_thumbnail=True),
                   'caption': formish.Input(empty=''),
                   'publication_date': karlwidgets.DateTime(),
                   }
        return widgets

    def __call__(self):
        layout_provider = get_layout_provider(self.context, self.request)
        layout = layout_provider('generic')
        return {'api': self.api, 'layout': layout, 'actions': []}

    def handle_cancel(self):
        return HTTPFound(location=model_url(self.context, self.request))

    def handle_submit(self, converted):
        request = self.request
        context = self.context
        
        #create the news item and store it
        creator = authenticated_userid(request)
        newsitem = create_content(
            INewsItem,
            title=converted['title'],
            text=converted['text'],
            creator=creator,
            publication_date=converted['publication_date'],
            caption=converted['caption'],
            )
        name = make_unique_name(context, converted['title'])
        context[name] = newsitem

        # tags, attachments, and photos
        set_tags(newsitem, request, converted['tags'])
        attachments_folder = newsitem['attachments']
        upload_attachments(converted['attachments'], attachments_folder,
                           creator, request)
        handle_photo_upload(newsitem, converted)
        self.filestore.clear()

        location = model_url(newsitem, request)
        return HTTPFound(location=location)

def newsitem_photo_filestore_view(context, request):
    return photo_from_filestore_view(context, request, 'newsitem')

# XXX Needs unittest
def show_newsitem_view(context, request):
    backto = {
        'href': model_url(context.__parent__, request),
        'title': context.__parent__.title,
        }

    actions = []
    if has_permission('create', context, request):
        actions.append(
            ('Edit', 'edit.html')
            )
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

    # Display photo
    photo = context.get_photo()
    if photo is not None:
        photo = {
            "url": model_url(photo, request),
        }

    # Get a layout
    layout_provider = get_layout_provider(context, request)
    layout = layout_provider('generic')

    return render_template_to_response(
        'templates/show_newsitem.pt',
        api=api,
        actions=actions,
        attachments=fetch_attachments(context['attachments'], request),
        formfields=api.formfields,
        head_data=convert_to_script(client_json_data),
        backto=backto,
        previous=previous,
        next=next,
        layout=layout,
        photo=photo,
        )

class EditNewsItemFormController(AddNewsItemFormController):
    def __init__(self, context, request):
        self.page_title = 'Edit %s' % context.title
        super(EditNewsItemFormController, self).__init__(context, request)
        photo = context.get_photo()
        if photo is not None:
            photo = SchemaFile(None, photo.__name__, photo.mimetype)
        self.photo = photo

    def form_defaults(self):
        context = self.context
        attachments = [SchemaFile(None, x.__name__, x.mimetype)
                       for x in context['attachments'].values()]
        defaults = {
            'title': context.title,
            'tags': [], # initial values supplied by widget
            'text': context.text,
            'attachments': attachments,
            'photo': self.photo,
            'caption': context.caption,
            'publication_date': context.publication_date,
            }
        return defaults

    def form_widgets(self, fields):
        tagdata = get_tags_client_data(self.context, self.request)
        default_icon = '%s/images/image.png' % self.api.static_url
        widgets = {'title': formish.Input(empty=''),
                   'tags': karlwidgets.TagsEditWidget(tagdata=tagdata),
                   'text': karlwidgets.RichTextWidget(empty=''),
                   'attachments': formish.SequenceDefault(sortable=False),
                   'attachments.*': karlwidgets.FileUpload2(
                       filestore=self.filestore),
                   'photo': karlwidgets.PhotoImageWidget(
                       filestore=self.filestore,
                       url_base=model_url(self.context, self.request),
                       show_image_thumbnail=True,
                       show_remove_checkbox=self.photo is not None),
                   'caption': formish.Input(empty=''),
                   'publication_date': karlwidgets.DateTime(),
                   }
        return widgets

    def handle_submit(self, converted):
        request = self.request
        context = self.context

        # *will be* modified event
        objectEventNotify(ObjectWillBeModifiedEvent(context))

        simple_fields = ['title', 'text', 'caption', 'publication_date']
        for field in simple_fields:
            setattr(context, field, converted[field])

        # save tags, attachments, photo
        set_tags(context, request, converted['tags'])
        userid = authenticated_userid(request)
        attachments_folder = context['attachments']
        upload_attachments(converted['attachments'], attachments_folder,
                           userid, request)
        handle_photo_upload(context, converted)
        self.filestore.clear

        # mark as modified
        context.modified_by = userid
        objectEventNotify(ObjectModifiedEvent(context))

        location = model_url(context, request)
        msg = "?status_message=News%20Item%20edited"
        return HTTPFound(location=location+msg)

