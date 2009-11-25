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
from formencode import validators

from webob.exc import HTTPFound
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component.event import objectEventNotify

from repoze.bfg.chameleon_zpt import render_template
from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.security import authenticated_userid
from repoze.bfg.security import has_permission
from repoze.bfg.url import model_url

from repoze.enformed import FormSchema

from repoze.lemonade.content import create_content

from karl.events import ObjectModifiedEvent
from karl.events import ObjectWillBeModifiedEvent

from karl.views import baseforms
from karl.views.api import TemplateAPI
from karl.views.form import render_form_to_response
from karl.views.interfaces import IFolderAddables
from karl.views.tags import set_tags
from karl.views.utils import convert_to_script
from karl.views.tags import get_tags_client_data
from karl.views.utils import make_unique_name

from karl.content.interfaces import ICommunityFile
from karl.content.interfaces import IPage
from karl.content.interfaces import IReferenceManual
from karl.content.interfaces import IReferenceSection
from karl.content.views.interfaces import IFileInfo
from karl.content.views.utils import get_previous_next

from karl.utils import get_layout_provider

def add_referencemanual_view(context, request):
    tags_list=request.POST.getall('tags')
    form = AddReferenceManualForm(tags_list=tags_list)

    if 'form.cancel' in request.POST:
        return HTTPFound(location=model_url(context, request))

    if 'form.submitted' in request.POST:
        try:
            converted = form.validate(request.POST)
            # Create the reference manual and store it
            creator = authenticated_userid(request)
            reference_manual = create_content(IReferenceManual,
                                              converted['title'],
                                              converted['description'],
                                              creator,
                                              )
            name = make_unique_name(context, converted['title'])
            context[name] = reference_manual

            # Save the tags on it.
            set_tags(reference_manual, request, converted['tags'])

            location = model_url(reference_manual, request)
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
    page_title = 'Add Reference Manual'
    api = TemplateAPI(context, request, page_title)

    # Get a layout
    layout_provider = get_layout_provider(context, request)
    layout = layout_provider('intranet')

    return render_form_to_response(
        'templates/addedit_referencemanual.pt',
        form,
        fill_values,
        post_url=request.url,
        formfields=api.formfields,
        fielderrors=fielderrors,
        api=api,
        head_data=convert_to_script(dict(
                tags_field = tags_field,
            )),
        layout=layout,
        )

def _get_toc(context, here_url):
    """Get the nested data used by ZPT for showing the refman TOC"""
    section_up = here_url + '?sectionUp=%s'
    section_down = here_url + '?sectionDown=%s'
    item_up = here_url + '?section=%s&itemUp=%s'
    item_down = here_url + '?section=%s&itemDown=%s'

    # First, be a chicken and sync
    context.ordering.sync(context.keys())

    # Iterate over each section using the ordering for the order of
    # __name__'s
    sections = []
    for section_name in context.ordering.items():
        # Get the data about this section
        section = context.get(section_name)
        section.ordering.sync(section.keys())
        item = {
            'name': section_name,
            'title': section.title,
            'moveUp': section_up % section_name,
            'moveDown': section_down % section_name,
            'href': here_url + section_name,
            'items': [],
            }
        # Now append data about each section's items, again using the
        # ordering
        for subitem_name in section.ordering.items():
            subitem = section.get(subitem_name)
            item['items'].append({
                'name': subitem_name,
                'title': subitem.title,
                 'href': here_url + section_name + '/' + subitem_name,
                 'moveUp': item_up % (section_name, subitem_name),
                 'moveDown': item_down % (section_name, subitem_name),
                 })

        sections.append(item)

    return sections


def _get_viewall(context, request, api):
    """Get the nested data used by ZPT for showing the refman TOC"""

    # First, be a chicken and sync
    context.ordering.sync(context.keys())

    # Iterate over each section using the ordering for the order of
    # __name__'s
    sections = []
    for section_name in context.ordering.items():
        # Get the data about this section
        section = context.get(section_name)
        section.ordering.sync(section.keys())
        item = {
            'name': section_name,
            'title': section.title,
            'html': '<p>%s</p>' % section.description,
            'items': [],
            }
        # Now append data about each section's items, again using the
        # ordering
        for subitem_name in section.ordering.items():
            subitem = section.get(subitem_name)

            # If this is a page, we generate one chunk of HTML, if
            # File, a different
            if IPage.providedBy(subitem):
                html = subitem.text
            elif ICommunityFile.providedBy(subitem):
                fileinfo = getMultiAdapter((subitem, request), IFileInfo)
                html = render_template(
                    'templates/inline_file.pt',
                    api=api,
                    fileinfo=fileinfo,
                    )
            else:
                html = '<p>Unknown type</p>'
            item['items'].append({
                'name': subitem_name,
                'title': subitem.title,
                'html': html,
                 })

        sections.append(item)

    return sections



def show_referencemanual_view(context, request):

    # Look for moveUp or moveDown in QUERY_STRING, telling us to
    # reorder something
    status_message = None
    sectionUp = request.params.get('sectionUp', False)
    if sectionUp:
        section = context.get(sectionUp)
        context.ordering.moveUp(sectionUp)
        status_message = 'Moved section <em>%s</em> up' % section.title
    else:
        sectionDown = request.params.get('sectionDown', False)
        if sectionDown:
            section = context.get(sectionDown)
            context.ordering.moveDown(sectionDown)
            status_message = 'Moved section <em>%s</em> down' % section.title
        else:
            itemUp = request.params.get('itemUp', False)
            if itemUp:
                section = context.get(request.params.get('section'))
                section.ordering.moveUp(itemUp)
                title = section.get(itemUp).title
                status_message = 'Moved item <em>%s</em> up' % title
            else:
                itemDown = request.params.get('itemDown', False)
                if itemDown:
                    section = context.get(request.params.get('section'))
                    section.ordering.moveDown(itemDown)
                    title = section.get(itemDown).title
                    status_message = 'Moved item <em>%s</em> down' % title

    backto = {
        'href': model_url(context.__parent__, request),
        'title': context.__parent__.title,
        }

    actions = []
    if has_permission('create', context, request):
        addables = queryMultiAdapter((context, request), IFolderAddables)
        if addables is not None:
            actions.extend(addables())
        actions.append(('Edit', 'edit.html'))
        if has_permission('delete', context, request):
            actions.append(('Delete', 'delete.html'))

    page_title = context.title
    api = TemplateAPI(context, request, page_title)

    # Get a layout
    layout_provider = get_layout_provider(context, request)
    layout = layout_provider('intranet')

    # provide client data for rendering current tags in the tagbox
    client_json_data = dict(
        tagbox = get_tags_client_data(context, request),
        )

    api.status_message = status_message
    return render_template_to_response(
        'templates/show_referencemanual.pt',
        api=api,
        actions=actions,
        head_data=convert_to_script(client_json_data),
        sections=_get_toc(context, api.here_url),
        backto=backto,
        layout=layout,
        )


def viewall_referencemanual_view(context, request):

    backto = {
        'href': model_url(context.__parent__, request),
        'title': context.__parent__.title,
        }

    page_title = context.title
    api = TemplateAPI(context, request, page_title)

    # Get a layout
    layout_provider = get_layout_provider(context, request)
    layout = layout_provider('intranet')

    # provide client data for rendering current tags in the tagbox
    client_json_data = dict(
        tagbox = get_tags_client_data(context, request),
        )

    return render_template_to_response(
        'templates/viewall_referencemanual.pt',
        api=api,
        actions=[],
        head_data=convert_to_script(client_json_data),
        sections=_get_viewall(context, request, api),
        backto=backto,
        layout=layout,
        )


def edit_referencemanual_view(context, request):

    tags_list = request.POST.getall('tags')
    form = EditReferenceManualForm(tags_list=tags_list)

    if 'form.cancel' in request.POST:
        return HTTPFound(location=model_url(context, request))

    if 'form.submitted' in request.POST:
        try:
            converted = form.validate(request.POST)
            # *will be* modified event
            objectEventNotify(ObjectWillBeModifiedEvent(context))

            context.title = converted['title']
            context.description = converted['description']

            # Save the tags on it
            set_tags(context, request, converted['tags'])

            # Modified
            context.modified_by = authenticated_userid(request)
            objectEventNotify(ObjectModifiedEvent(context))

            location = model_url(context, request)
            msg = "?status_message=Reference%20manual%20edited"
            return HTTPFound(location=location+msg)

        except Invalid, e:
            fielderrors = e.error_dict
            fill_values = form.convert(request.POST)
    else:
        fielderrors = {}
        fill_values = dict(
            title = context.title,
            description = context.description,
            )

    # prepare client data
    client_json_data = dict(
        tags_field = get_tags_client_data(context, request),
    )

    # Render the form and shove some default values in
    page_title = 'Edit ' + context.title
    api = TemplateAPI(context, request, page_title)

    # Get a layout
    layout_provider = get_layout_provider(context, request)
    layout = layout_provider('intranet')

    return render_form_to_response(
        'templates/addedit_referencemanual.pt',
        form,
        fill_values,
        post_url=request.url,
        formfields=api.formfields,
        fielderrors=fielderrors,
        api=api,
        head_data=convert_to_script(client_json_data),
        layout=layout,
        )



def add_referencesection_view(context, request):

    tags_list=request.POST.getall('tags')
    form = AddReferenceSectionForm(tags_list = tags_list)

    if 'form.cancel' in request.POST:
        return HTTPFound(location=model_url(context, request))

    if 'form.submitted' in request.POST:
        try:
            converted = form.validate(request.POST)

            # Be a chicken and sync the ordering every time before
            # adding something, just to make sure nothing gets lost.
            context.ordering.sync(context.keys())

            # Create the reference section and store it
            creator = authenticated_userid(request)
            reference_section = create_content(IReferenceSection,
                                               converted['title'],
                                               converted['description'],
                                               creator,
                                               )
            name = make_unique_name(context, converted['title'])
            context[name] = reference_section

            # Save the tags on it.
            set_tags(reference_section, request, converted['tags'])

            # Update the ordering
            context.ordering.add(name)

            location = model_url(reference_section, request)
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
    page_title = 'Add Reference Section'
    api = TemplateAPI(context, request, page_title)

    # Get a layout
    layout_provider = get_layout_provider(context, request)
    layout = layout_provider('intranet')

    return render_form_to_response(
        'templates/addedit_referencesection.pt',
        form,
        fill_values,
        post_url=request.url,
        formfields=api.formfields,
        fielderrors=fielderrors,
        api=api,
        head_data=convert_to_script(dict(
                tags_field = tags_field,
            )),
        layout=layout,
        )


def _get_ordered_listing(context, request):

    # First, be a chicken and sync
    context.ordering.sync(context.keys())

    # Flatten the list
    entries = []
    for name in context.ordering.items():
        child = context.get(name, False)
        entries.append({
                'title': child.title,
                'href': model_url(child, request),
                })
    return entries

def show_referencesection_view(context, request):

    backto = {
        'href': model_url(context.__parent__, request),
        'title': context.__parent__.title,
        }

    actions = []
    if has_permission('create', context, request):
        addables = queryMultiAdapter((context, request), IFolderAddables)
        if addables is not None:
            actions.extend(addables())
        actions.append(('Edit', 'edit.html'))
        if has_permission('delete', context, request):
            actions.append(('Delete', 'delete.html'))

    page_title = context.title
    api = TemplateAPI(context, request, page_title)

    # Get a layout
    layout_provider = get_layout_provider(context, request)
    layout = layout_provider('intranet')

    previous, next = get_previous_next(context, request)

    # provide client data for rendering current tags in the tagbox
    client_json_data = dict(
        tagbox = get_tags_client_data(context, request),
        )

    return render_template_to_response(
        'templates/show_referencesection.pt',
        api=api,
        actions=actions,
        entries=_get_ordered_listing(context, request),
        head_data=convert_to_script(client_json_data),
        backto=backto,
        previous=previous,
        next=next,
        layout=layout,
        )

def edit_referencesection_view(context, request):

    tags_list = request.POST.getall('tags')
    form = EditReferenceSectionForm(tags_list=tags_list)

    if 'form.cancel' in request.POST:
        return HTTPFound(location=model_url(context, request))

    if 'form.submitted' in request.POST:
        try:
            converted = form.validate(request.POST)
            # *will be* modified event
            objectEventNotify(ObjectWillBeModifiedEvent(context))

            context.title = converted['title']
            context.description = converted['description']

            # Save the tags on it
            set_tags(context, request, converted['tags'])

            # Modified
            context.modified_by = authenticated_userid(request)
            objectEventNotify(ObjectModifiedEvent(context))

            location = model_url(context, request)
            msg = "?status_message=Reference%20section%20edited"
            return HTTPFound(location=location+msg)

        except Invalid, e:
            fielderrors = e.error_dict
            fill_values = form.convert(request.POST)
    else:
        fielderrors = {}
        fill_values = dict(
            title = context.title,
            description = context.description,
            )

    # prepare client data
    client_json_data = dict(
        tags_field = get_tags_client_data(context, request),
    )

    # Render the form and shove some default values in
    page_title = 'Edit ' + context.title
    api = TemplateAPI(context, request, page_title)

    # Get a layout
    layout_provider = get_layout_provider(context, request)
    layout = layout_provider('intranet')

    return render_form_to_response(
        'templates/addedit_referencesection.pt',
        form,
        fill_values,
        post_url=request.url,
        formfields=api.formfields,
        fielderrors=fielderrors,
        api=api,
        head_data=convert_to_script(client_json_data),
        layout=layout,
        )



class AddReferenceManualForm(FormSchema):
    title = baseforms.title
    tags = baseforms.tags
    description = validators.UnicodeString(strip=True)

class EditReferenceManualForm(FormSchema):
    title = baseforms.title
    tags = baseforms.tags
    description = validators.UnicodeString(strip=True)

class AddReferenceSectionForm(FormSchema):
    title = baseforms.title
    tags = baseforms.tags
    description = validators.UnicodeString(strip=True)

class EditReferenceSectionForm(FormSchema):
    title = baseforms.title
    tags = baseforms.tags
    description = validators.UnicodeString(strip=True)

