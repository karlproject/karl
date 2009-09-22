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
from zope.component import getMultiAdapter

from formencode import Invalid

from repoze.bfg.chameleon_zpt import render_template_to_response

from repoze.bfg.url import model_url
from repoze.bfg.security import authenticated_userid
from repoze.bfg.security import has_permission

from repoze.enformed import FormSchema

from repoze.lemonade.content import create_content

from karl.content.interfaces import INewsItem

from karl.events import ObjectModifiedEvent
from karl.events import ObjectWillBeModifiedEvent

from karl.views.api import TemplateAPI
from karl.views import baseforms

from karl.views.utils import convert_to_script
from karl.views.utils import make_unique_name
from karl.views.form import render_form_to_response
from karl.views.tags import set_tags
from karl.views.tags import get_tags_client_data
from karl.views.utils import handle_photo_upload

from karl.views.interfaces import ILayoutProvider
from karl.content.views.utils import get_previous_next
from karl.content.views.utils import store_attachments
from karl.content.views.utils import fetch_attachments

import datetime

_NOW = None

def _now():
    if _NOW is not None:
        return _NOW
    return datetime.datetime.now()

def add_newsitem_view(context, request):

    tags_list=request.POST.getall('tags')
    form = NewsItemForm(tags_list=tags_list)

    if 'form.cancel' in request.POST:
        return HTTPFound(location=model_url(context, request))

    if 'form.submitted' in request.POST:
        try:
            converted = form.validate(request.POST)

            # Create the resource and store it
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

            # Tags, attachments and photos
            set_tags(newsitem, request, converted['tags'])
            store_attachments(newsitem['attachments'], request.params, creator)
            handle_photo_upload(newsitem, converted)

            location = model_url(newsitem, request)
            return HTTPFound(location=location)

        except Invalid, e:
            fielderrors = e.error_dict
            fill_values = form.convert(request.POST)
            if 'photo' in fill_values:
                del fill_values['photo'] # render cant hack it
            tags_field = dict(
                records = [dict(tag=t) for t in request.POST.getall('tags')]
                )

    else:
        fielderrors = {}
        tags_field = dict(records=[])
        now = _now()
        fill_values =  dict(
            publication_date = now,
            )

    # Render the form and shove some default values in
    page_title = 'Add News Item'
    api = TemplateAPI(context, request, page_title)

    # Display photo
    photo = {
        "may_delete": False,
    }

    # Get a layout
    layout_provider = getMultiAdapter((context, request), ILayoutProvider)
    layout = layout_provider('generic')

    return render_form_to_response(
        'templates/addedit_newsitem.pt',
        form,
        fill_values,
        post_url=request.url,
        formfields=api.formfields,
        fielderrors=fielderrors,
        api=api,
        photo=photo,
        head_data=convert_to_script(dict(
                tags_field = tags_field,
                )),
        layout=layout,
        )

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
    layout_provider = getMultiAdapter((context, request), ILayoutProvider)
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


def edit_newsitem_view(context, request):

    tags_list = request.POST.getall('tags')
    form = EditNewsItemForm(tags_list=tags_list)

    if 'form.cancel' in request.POST:
        return HTTPFound(location=model_url(context, request))

    if 'form.submitted' in request.POST:
        try:
            converted = form.validate(request.POST)

            # *will be* modified event
            objectEventNotify(ObjectWillBeModifiedEvent(context))

            context.title = converted['title']
            context.text = converted['text']
            context.caption = converted['caption']
            context.publication_date = converted['publication_date']

            # Save the tags on it
            set_tags(context, request, converted['tags'])

            creator = authenticated_userid(request)
            store_attachments(context['attachments'], request.params, creator)
            handle_photo_upload(context, converted)

            # Modified
            context.modified_by = authenticated_userid(request)
            objectEventNotify(ObjectModifiedEvent(context))

            location = model_url(context, request)
            msg = "?status_message=News%20Item%20edited"
            return HTTPFound(location=location+msg)

        except Invalid, e:
            fielderrors = e.error_dict
            fill_values = form.convert(request.POST)
            if 'photo' in fill_values:
                del fill_values['photo'] # render can't hack it
    else:
        fielderrors = {}
        fill_values = dict(
            title = context.title,
            text = context.text,
            caption = context.caption,
            publication_date = context.publication_date
            )

    # prepare client data
    client_json_data = dict(
        tags_field = get_tags_client_data(context, request),
        )

    # Render the form and shove some default values in
    page_title = 'Edit ' + context.title
    api = TemplateAPI(context, request, page_title)

    photo = context.get_photo()
    display_photo = {}
    if photo is not None:
        display_photo["url"] = model_url(photo, request)
        display_photo["may_delete"] = True
    else:
        display_photo["may_delete"] = False

    # Get a layout
    layout_provider = getMultiAdapter((context, request), ILayoutProvider)
    layout = layout_provider('generic')

    return render_form_to_response(
        'templates/addedit_newsitem.pt',
        form,
        fill_values,
        post_url=request.url,
        formfields=api.formfields,
        fielderrors=fielderrors,
        api=api,
        photo=display_photo,
        head_data=convert_to_script(client_json_data),
        layout=layout,
        )


class NewsItemForm(FormSchema):
    title = baseforms.title
    tags = baseforms.tags
    text = baseforms.text
    photo = baseforms.photo
    caption = baseforms.caption
    publication_date = baseforms.publication_date

class EditNewsItemForm(NewsItemForm):
    photo_delete = baseforms.photo_delete

