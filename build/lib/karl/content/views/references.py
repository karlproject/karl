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

from pyramid.httpexceptions import HTTPFound
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component.event import objectEventNotify
from zope.interface import implements

from validatish import validator
import formish
import schemaish

from pyramid.renderers import render
from pyramid.renderers import render_to_response
from pyramid.security import authenticated_userid
from pyramid.security import has_permission
from pyramid.url import resource_url
from repoze.lemonade.content import create_content

from karl.content.interfaces import IReferenceManual
from karl.content.interfaces import IReferenceManualHTML
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
from karl.utils import find_intranet


tags_field = schemaish.Sequence(schemaish.String())
description_field = schemaish.String(
    description="A summary of the reference manual - subject and scope. "
    "Will be displayed on every page of the manual.")

class DescriptionHTML(object):
    """ Adapter for sections.
    """
    implements(IReferenceManualHTML)

    def __init__(self, context, request):
        self.context = context
        self.request = context

    def __call__(self, api):
        return '<p>%s</p>' % self.context.description


class TextHTML(object):
    """ Adapter for pages.
    """
    implements(IReferenceManualHTML)

    def __init__(self, context, request):
        self.context = context
        self.request = context

    def __call__(self, api):
        return self.context.text


class FileHTML(object):
    """ Adapter for files.
    """
    implements(IReferenceManualHTML)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, api):
        fileinfo = getMultiAdapter((self.context, self.request), IFileInfo)
        return render(
            'templates/inline_file.pt',
            dict(api=api,
                 fileinfo=fileinfo),
            request=self.request,
            )


def getTree(root, request, api, _subpath_prefix='|'):
    """ Return a recursive structure describing roots descendants.

    - The result is a sequence of mappings, one per direct child of ``root``.

    - Each node in the structure describes one descendant.  Its children,
      if any, are in its ``items`` value.

    - Leaf nodes with have an empty tuple as their ``items`` value.

    - ``_subpath_prefix`` is not part of the API, but used only
      to manage building up the subpath recursively.
    """
    root.ordering.sync(root.keys())
    result = []
    for name in root.ordering.items():
        child = root[name]
        ordering = getattr(child, 'ordering', None)
        subpath = _subpath_prefix + child.__name__
        if ordering is not None:
            ordering.sync(child.keys())
            items = getTree(child, request, api, subpath + '|')
        else:
            items = () # tuple signals leaf
        html_adapter = queryMultiAdapter((child, request), IReferenceManualHTML)
        html = html_adapter and html_adapter(api) or '<p>Unknown type</p>'
        item = {'name': name,
                'title': child.title,
                'href': resource_url(child, request),
                'html': html,
                'subpath': subpath,
                'items': items,
               }
        result.append(item)
    return result


def move_subpath(context, subpath, direction):
    elements = subpath.split('|')
    container = context
    assert elements[0] == '' # start at context
    elements.pop(0)
    filename = None
    while elements:
        container.ordering.sync(container.keys())
        name = elements.pop(0)
        if elements:
            container = container[name]
    if name not in container:
        raise KeyError(name)
    if direction == 'up':
        container.ordering.moveUp(name)
    elif direction == 'down':
        container.ordering.moveDown(name)
    else:
        raise ValueError('Unknown direction: %' % direction)
    return 'Moved subpath %s %s' % (subpath, direction)


def reference_outline_view(context, request):

    # Look for moveUp or moveDown in QUERY_STRING, telling us to
    # reorder something
    status_message = None
    subpath = request.params.get('subpath')

    backto = {
        'href': resource_url(context.__parent__, request),
        'title': context.__parent__.title,
        }

    user_can_edit = False
    actions = []
    if has_permission('create', context, request):
        addables = get_folder_addables(context, request)
        if addables is not None:
            actions.extend(addables())
    if has_permission('edit', context, request):
        user_can_edit = True
        actions.append(('Edit', 'edit.html'))
        if subpath:
            direction = request.params['direction']
            status_message = move_subpath(context, subpath, direction)
    if has_permission('delete', context, request):
        actions.append(('Delete', 'delete.html'))
    if has_permission('administer', context, request):
        actions.append(('Advanced', 'advanced.html'))

    page_title = context.title
    api = TemplateAPI(context, request, page_title)

    # Get a layout
    layout_provider = get_layout_provider(context, request)
    old_layout = layout_provider('intranet')

    # provide client data for rendering current tags in the tagbox
    client_json_data = dict(
        tagbox = get_tags_client_data(context, request),
        )

    previous, next = get_previous_next(context, request)

    intranet = find_intranet(context)
    if intranet is not None:
        ux2_layout = request.layout_manager.layout
        ux2_layout.section_style = "none"

    api.status_message = status_message
    return render_to_response(
        'templates/show_referencemanual.pt',
        dict(api=api,
             actions=actions,
             user_can_edit=user_can_edit,
             head_data=convert_to_script(client_json_data),
             tree=getTree(context, request, api),
             backto=backto,
             old_layout=old_layout,
             previous_entry=previous,
             next_entry=next),
        request=request,
        )


def reference_viewall_view(context, request):

    backto = {
        'href': resource_url(context.__parent__, request),
        'title': context.__parent__.title,
        }

    actions = []
    if has_permission('create', context, request):
        addables = get_folder_addables(context, request)
        if addables is not None:
            actions.extend(addables())
    if has_permission('edit', context, request):
        actions.append(('Edit', 'edit.html'))
    if has_permission('delete', context, request):
        actions.append(('Delete', 'delete.html'))
    if has_permission('administer', context, request):
        actions.append(('Advanced', 'advanced.html'))

    page_title = context.title
    api = TemplateAPI(context, request, page_title)

    # Get a layout
    layout_provider = get_layout_provider(context, request)
    old_layout = layout_provider('intranet')

    # provide client data for rendering current tags in the tagbox
    client_json_data = dict(
        tagbox = get_tags_client_data(context, request),
        )

    previous, next = get_previous_next(context, request, 'view_all.html')

    intranet = find_intranet(context)
    if intranet is not None:
        ux2_layout = request.layout_manager.layout
        ux2_layout.section_style = "none"

    return render_to_response(
        'templates/viewall_referencemanual.pt',
        dict(api=api,
             actions=actions,
             head_data=convert_to_script(client_json_data),
             tree=getTree(context, request, api),
             backto=backto,
             old_layout=old_layout,
             previous_entry=previous,
             next_entry=next),
        request=request,
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
                'href': resource_url(child, request),
                })
    return entries


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
        intranet = find_intranet(self.context)
        if intranet is not None:
            ux2_layout = self.request.layout_manager.layout
            ux2_layout.section_style = "none"

        return {
            'api': api,             # deprecated UX1
            'old_layout': layout,   # deprecated UX1
            'actions': []}          # deprecated UX1

    def handle_cancel(self):
        return HTTPFound(location=resource_url(self.context, self.request))

    def handle_submit(self, converted):
        request = self.request
        context = self.context
        ordering = getattr(context, 'ordering', None)
        if ordering is not None:
            ordering.sync(context.keys())

        creator = authenticated_userid(request)
        reference_object = create_content(self.content_iface,
                                          converted['title'],
                                          converted['description'],
                                          creator,
                                          )
        name = make_unique_name(context, converted['title'])
        context[name] = reference_object

        if ordering is not None:
            ordering.add(name)

        # save the tags
        set_tags(reference_object, request, converted['tags'])

        location = resource_url(reference_object, request)
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
        intranet = find_intranet(self.context)
        if intranet is not None:
            ux2_layout = self.request.layout_manager.layout
            ux2_layout.section_style = "none"
        return {
            'api': api,             # deprecated UX1
            'old_layout': layout,   # deprecated UX1
            'actions': []}          # deprecated UX1

    def handle_cancel(self):
        return HTTPFound(location=resource_url(self.context, self.request))

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
        location = resource_url(context, request)
        msg = "?status_message=%s" % self.success_msg
        return HTTPFound(location='%s%s' % (location, msg))


class EditReferenceManualFormController(EditReferenceFCBase):
    success_msg = 'Reference%20manual%20edited'


class EditReferenceSectionFormController(EditReferenceFCBase):
    success_msg = 'Reference%20section%20edited'
