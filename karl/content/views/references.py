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
from zope.component import getMultiAdapter
from zope.component.event import objectEventNotify

from validatish import validator
import formish
import schemaish

from repoze.bfg.chameleon_zpt import render_template
from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.security import authenticated_userid
from repoze.bfg.security import has_permission
from repoze.bfg.url import model_url
from repoze.lemonade.content import create_content

from karl.content.interfaces import ICommunityFile
from karl.content.interfaces import IPage
from karl.content.interfaces import IReferenceManual
from karl.content.interfaces import IReferenceSection
from karl.content.views.interfaces import IFileInfo
from karl.content.views.utils import get_previous_next
from karl.events import ObjectModifiedEvent
from karl.events import ObjectWillBeModifiedEvent
from karl.views.api import TemplateAPI
from karl.views.forms import widgets as karlwidgets
from karl.views.tags import get_tags_client_data
from karl.views.tags import set_tags
from karl.views.utils import convert_to_script
from karl.views.utils import make_unique_name
from karl.utils import get_folder_addables
from karl.utils import get_layout_provider


tags_field = schemaish.Sequence(schemaish.String())
description_field = schemaish.String(
    description="A summary of the reference manual - subject and scope. "
    "Will be displayed on every page of the manual.")


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
        addables = get_folder_addables(context, request)
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
        addables = get_folder_addables(context, request)
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


class AddReferenceFCBase(object):
    """Base class for the form controllers for adding a reference
    manual and a reference section, since they are very similar."""
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def form_fields(self):
        title_field = schemaish.String(
            validator=validator.All(
                validator.Length(max=100),
                validator.Required(),
                ))
        fields = [('title', title_field),
                  ('tags', tags_field),
                  ('description', description_field),
                  ]
        return fields

    def form_widgets(self, fields):
        widgets = {'title': formish.Input(empty=''),
                   'tags': karlwidgets.TagsAddWidget(),
                   'description': formish.TextArea(rows=5, cols=60, empty=''),
                   }
        return widgets

    def __call__(self):
        context = self.context
        request = self.request
        api = TemplateAPI(context, request, self.page_title)

        layout_provider = get_layout_provider(context, request)
        layout = layout_provider('intranet')
        return {'api': api, 'layout': layout, 'actions': []}

    def handle_cancel(self):
        return HTTPFound(location=model_url(self.context, self.request))

    def handle_submit(self, converted):
        request = self.request
        context = self.context
        creator = authenticated_userid(request)
        reference_object = create_content(self.content_iface,
                                          converted['title'],
                                          converted['description'],
                                          creator,
                                          )
        name = make_unique_name(context, converted['title'])
        context[name] = reference_object
        context.ordering.sync(context.keys())
        context.ordering.add(name)
        # save the tags
        set_tags(reference_object, request, converted['tags'])

        location = model_url(reference_object, request)
        return HTTPFound(location=location)


class AddReferenceManualFormController(AddReferenceFCBase):
    page_title = u'Add Reference Manual'
    content_iface = IReferenceManual


class AddReferenceSectionFormController(AddReferenceFCBase):
    page_title = u'Add Reference Section'
    content_iface = IReferenceSection


class EditReferenceFCBase(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def form_defaults(self):
        context = self.context
        defaults = {'title': context.title,
                    'tags': [], # initial values supplied by widget
                    'description': context.description,
                    }
        return defaults

    def form_fields(self):
        title_field = schemaish.String(
            validator=validator.All(
                validator.Length(max=100),
                validator.Required(),
                ))
        fields = [('title', title_field),
                  ('tags', tags_field),
                  ('description', description_field),
                  ]
        return fields

    def form_widgets(self, fields):
        tagdata = get_tags_client_data(self.context, self.request)
        widgets = {'title': formish.Input(empty=''),
                   'tags': karlwidgets.TagsEditWidget(tagdata=tagdata),
                   'description': formish.TextArea(rows=5, cols=60, empty=''),
                   }
        return widgets

    def __call__(self):
        context = self.context
        request = self.request
        page_title = 'Edit %s' % context.title
        api = TemplateAPI(context, request, page_title)

        layout_provider = get_layout_provider(context, request)
        layout = layout_provider('intranet')
        return {'api': api, 'layout': layout, 'actions': []}

    def handle_cancel(self):
        return HTTPFound(location=model_url(self.context, self.request))

    def handle_submit(self, converted):
        context = self.context
        request = self.request
        # *will be* modified event
        objectEventNotify(ObjectWillBeModifiedEvent(context))

        context.title = converted['title']
        context.description = converted['description']
        # save the tags
        set_tags(context, request, converted['tags'])

        # modified
        context.modified_by = authenticated_userid(request)
        objectEventNotify(ObjectModifiedEvent(context))
        location = model_url(context, request)
        msg = "?status_message=%s" % self.success_msg
        return HTTPFound(location='%s%s' % (location, msg))


class EditReferenceManualFormController(EditReferenceFCBase):
    success_msg = 'Reference%20manual%20edited'


class EditReferenceSectionFormController(EditReferenceFCBase):
    success_msg = 'Reference%20section%20edited'
