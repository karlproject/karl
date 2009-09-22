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
from repoze.bfg.chameleon_zpt import render_template

from repoze.bfg.url import model_url
from repoze.bfg.security import authenticated_userid
from repoze.bfg.security import has_permission

from repoze.enformed import FormSchema

from repoze.lemonade.content import create_content

from karl.content.interfaces import IPage

from karl.events import ObjectModifiedEvent
from karl.events import ObjectWillBeModifiedEvent
from karl.utils import find_community

from karl.views.api import TemplateAPI
from karl.views import baseforms

from karl.views.form import render_form_to_response
from karl.views.utils import convert_to_script
from karl.views.utils import make_unique_name
from karl.views.tags import set_tags
from karl.views.tags import get_tags_client_data

from karl.content.views.utils import extract_description
from karl.views.interfaces import ILayoutProvider
from karl.content.views.utils import get_previous_next
from karl.content.views.utils import store_attachments
from karl.content.views.utils import fetch_attachments


def add_page_view(context, request):
    tags_list=request.POST.getall('tags')
    form = AddPageForm(tags_list=tags_list)

    if 'form.cancel' in request.POST:
        return HTTPFound(location=model_url(context, request))

    if 'form.submitted' in request.POST:
        try:
            converted = form.validate(request.POST)
            # Create the page and store it
            creator = authenticated_userid(request)
            page = create_content(IPage,
                                  converted['title'],
                                  converted['text'],
                                  extract_description(converted['text']),
                                  creator,
                                  )
            name = make_unique_name(context, converted['title'])
            context[name] = page

            # Tags and attachments
            set_tags(page, request, converted['tags'])
            store_attachments(page['attachments'], request.params, creator)

            # Update ordering if in ordered container
            if hasattr(context, 'ordering'):
                context.ordering.add(name)
                
            location = model_url(page, request)
            return HTTPFound(location=location)

        except Invalid, e:
            fielderrors = e.error_dict
            fill_values = form.convert(request.POST)
            tags_field = dict(
                records = [dict(tag=t) for t in request.POST.getall('tags')]
                )

    else:
        fielderrors = {}
        fill_values = {}
        tags_field = dict(records=[])

    # Render the form and shove some default values in
    page_title = 'Add Page'
    api = TemplateAPI(context, request, page_title)

    # Get a layout
    community = find_community(context)
    layout_provider = getMultiAdapter((context, request), ILayoutProvider)
    if community is not None:
        layout = layout_provider('community')
    else:
        layout = layout_provider('generic')
        
    return render_form_to_response(
        'templates/addedit_page.pt',
        form,
        fill_values,
        post_url=request.url,
        formfields=api.formfields,
        fielderrors=fielderrors,
        api=api,
        form=form,
        head_data=convert_to_script(dict(
                tags_field = tags_field,
                )),
        layout=layout,
        )

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
    layout_provider = getMultiAdapter((context, request), ILayoutProvider)
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


def edit_page_view(context, request):

    tags_list = request.POST.getall('tags')
    form = EditPageForm(tags_list=tags_list)

    if 'form.cancel' in request.POST:
        return HTTPFound(location=model_url(context, request))

    if 'form.submitted' in request.POST:
        try:
            converted = form.validate(request.POST)
            # *will be* modified event
            objectEventNotify(ObjectWillBeModifiedEvent(context))

            context.title = converted['title']
            context.text = converted['text']
            context.description = extract_description(converted['text'])

            # Save the tags on it
            set_tags(context, request, converted['tags'])

            # Save new attachments
            creator = authenticated_userid(request)
            store_attachments(context['attachments'], request.params, creator)

            # Modified
            context.modified_by = authenticated_userid(request)
            objectEventNotify(ObjectModifiedEvent(context))

            location = model_url(context, request)
            msg = "?status_message=Page%20edited"
            return HTTPFound(location=location+msg)

        except Invalid, e:
            fielderrors = e.error_dict
            fill_values = form.convert(request.POST)
    else:
        fielderrors = {}
        fill_values = dict(
            title = context.title,
            text = context.text,
            )

    # prepare client data
    client_json_data = dict(
        tags_field = get_tags_client_data(context, request),
        )

    # Render the form and shove some default values in
    page_title = 'Edit ' + context.title
    api = TemplateAPI(context, request, page_title)

    # Get a layout
    community = find_community(context)
    layout_provider = getMultiAdapter((context, request), ILayoutProvider)
    if community is not None:
        layout = layout_provider('community')
    else:
        layout = layout_provider('generic')

    return render_form_to_response(
        'templates/addedit_page.pt',
        form,
        fill_values,
        post_url=request.url,
        formfields=api.formfields,
        fielderrors=fielderrors,
        api=api,
        head_data=convert_to_script(client_json_data),
        layout=layout,
        )

class AddPageForm(FormSchema):
    title = baseforms.title
    tags = baseforms.tags
    text = baseforms.text

class EditPageForm(FormSchema):
    title = baseforms.title
    tags = baseforms.tags
    text = baseforms.text

