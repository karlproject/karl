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

import mimetypes
from simplejson import JSONEncoder

from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component.event import objectEventNotify
from zope.component import queryUtility
from zope.interface import alsoProvides
from zope.interface import noLongerProvides

from webob import Response
from webob.exc import HTTPFound

from formencode import Invalid

from repoze.bfg.chameleon_zpt import render_template_to_response

from repoze.bfg.security import authenticated_userid
from repoze.bfg.security import has_permission
from repoze.bfg.url import model_url
from repoze.workflow import get_workflow

from repoze.enformed import FormSchema

from repoze.lemonade.content import create_content

from karl.utilities.alerts import Alerts
from karl.utilities.interfaces import IAlerts

from karl.views.form import render_form_to_response
from karl.views.utils import make_name
from karl.views.utils import make_unique_name
from karl.views.utils import basename_of_filepath
from karl.views.utils import convert_to_script
from karl.views.tags import get_tags_client_data

from karl.views.api import TemplateAPI
from karl.views.baseforms import security_state as security_state_field
from karl.views.resource import delete_resource_view

from karl.events import ObjectModifiedEvent
from karl.events import ObjectWillBeModifiedEvent

from karl.content.interfaces import ICommunityFile
from karl.content.interfaces import ICommunityFolder
from karl.content.interfaces import ICommunityRootFolder
from karl.content.interfaces import IIntranetRootFolder

from karl.content.views.interfaces import IFileInfo
from karl.content.views.interfaces import IFolderCustomizer
from karl.content.views.interfaces import INetworkNewsMarker
from karl.content.views.interfaces import INetworkEventsMarker
from karl.content.views.interfaces import IShowSendalert

from karl.content.interfaces import IReferencesFolder

from karl.content.views.utils import get_previous_next

from karl.security.workflow import get_security_states

from karl.utils import get_folder_addables
from karl.utils import get_layout_provider

from karl.views import baseforms
from karl.views.tags import set_tags
from karl.views.batch import get_container_batch

from karl.views.utils import check_upload_size
from karl.views.utils import CustomInvalid

def show_folder_view(context, request):

    page_title = context.title
    api = TemplateAPI(context, request, page_title)

    # Now get the data that goes with this


    # Actions
    backto = False
    actions = []
    if has_permission('create', context, request):
        # Allow "policy" to override list of addables in a particular context
        addables = get_folder_addables(context, request)
        if addables is not None:
            actions.extend(addables())

    if not (ICommunityRootFolder.providedBy(context) or
        IIntranetRootFolder.providedBy(context)):
        # Root folders for the tools aren't editable or deletable
        if has_permission('create', context, request):
            actions.append(('Edit', 'edit.html'))
            actions.append(('Delete', 'delete.html'))
        if has_permission('administer', context, request):
            # admins see an Advanced action that puts markers on a
            # folder.
            actions.append(
                ('Advanced','advanced.html'),
                )
        backto = {
            'href': model_url(context.__parent__, request),
            'title': context.__parent__.title,
            }

    # Only provide atom feed links on root folder.
    if ICommunityRootFolder.providedBy(context):
        feed_url = model_url(context, request, "atom.xml")
    else:
        feed_url = None

    # Folder and tag data for Ajax
    client_json_data = dict(
        filegrid = get_filegrid_client_data(context, request,
                                            start = 0,
                                            limit = 10,
                                            sort_on = 'modified_date',
                                            reverse = True,
                                            ),
        tagbox = get_tags_client_data(context, request),
        )

    # Get a layout
    layout_provider = get_layout_provider(context, request)
    layout = layout_provider('community')

    return render_template_to_response(
        'templates/show_folder.pt',
        api=api,
        actions=actions,
        head_data=convert_to_script(client_json_data),
        backto=backto,
        layout=layout,
        feed_url=feed_url,
        )

def add_folder_view(context, request):
    tags_list=request.POST.getall('tags')
    form = AddFolderForm(tags_list=tags_list)
    workflow = get_workflow(ICommunityFolder, 'security', context)

    if workflow is None:
        security_states = []
    else:
        security_states = get_security_states(workflow, None, request)

    if security_states:
        form.add_field('security_state', security_state_field)

    if 'form.cancel' in request.POST:
        return HTTPFound(location=model_url(context, request))

    if 'form.submitted' in request.POST:
        try:
            converted = form.validate(request.POST)

            name = make_unique_name(context, converted['title'])
            creator = authenticated_userid(request)

            folder = create_content(ICommunityFolder,
                                    converted['title'],
                                    authenticated_userid(request),
                                    )
            context[name] = folder
            if workflow is not None:
                workflow.initialize(folder)
                if 'security_state' in converted:
                    workflow.transition_to_state(folder, request,
                                                 converted['security_state'])

            # Tags, attachments, alerts
            set_tags(folder, request, converted['tags'])

            # Make changes post-creation based on policy in src/osi
            customizer = queryMultiAdapter((folder, request), IFolderCustomizer)
            if customizer:
                for interface in customizer.markers:
                    alsoProvides(folder, interface)

            location = model_url(folder, request)
            return HTTPFound(location=location)

        except Invalid, e:
            fielderrors = e.error_dict
            fill_values = form.convert(request.POST)
            tags_field = dict(
                records = [dict(tag=t) for t in request.POST.getall('tags')]
                )
    else:
        fielderrors = {}
        if workflow is None:
            security_state = ''
        else:
            security_state = workflow.initial_state
        fill_values = dict(security_state=security_state)
        tags_field = dict(records=[])

    # Render the form and shove some default values in
    page_title = 'Add Folder'
    api = TemplateAPI(context, request, page_title)

    # Get a layout
    layout_provider = get_layout_provider(context, request)
    if layout_provider is None:
        layout = api.community_layout
    else:
        layout = layout_provider('community')


    return render_form_to_response(
        'templates/add_folder.pt',
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
        security_states = security_states,
        )

def delete_folder_view(context, request,
                       delete_resource_view=delete_resource_view):
    # delete_resource_view is passed as hook for unit testing
    return delete_resource_view(context, request, len(context))

def advanced_folder_view(context, request):

    page_title = 'Advanced Settings For ' + context.title
    api = TemplateAPI(context, request, page_title)

    if 'form.cancel' in request.POST:
        return HTTPFound(location=model_url(context, request))

    if 'form.submitted' in request.POST:
        marker = request.POST.get('marker', False)
        if marker == 'reference_manual':
            alsoProvides(context, IReferencesFolder)
            noLongerProvides(context, INetworkNewsMarker)
            noLongerProvides(context, INetworkEventsMarker)
        elif marker == 'network_news':
            alsoProvides(context, INetworkNewsMarker)
            noLongerProvides(context, IReferencesFolder)
            noLongerProvides(context, INetworkEventsMarker)
        elif marker == 'network_events':
            alsoProvides(context, INetworkEventsMarker)
            noLongerProvides(context, IReferencesFolder)
            noLongerProvides(context, INetworkNewsMarker)

        if marker:
            location = model_url(context, request, query=
                                 {'status_message': 'Marker changed'})
            return HTTPFound(location=location)

    # Get a layout
    layout_provider = get_layout_provider(context, request)
    layout = layout_provider('community')

    if IReferencesFolder.providedBy(context):
        selected = 'reference_manual'
    elif INetworkNewsMarker.providedBy(context):
        selected = 'network_news'
    elif INetworkEventsMarker.providedBy(context):
        selected = 'network_events'
    else:
        selected = None

    return render_template_to_response(
        'templates/advanced_folder.pt',
        api=api,
        actions=[],
        formfields=api.formfields,
        post_url=model_url(context, request, 'advanced.html'),
        layout=layout,
        fielderrors={},
        selected=selected,
        )

def add_file_view(context, request, check_upload_size=check_upload_size):

    tags_list=request.POST.getall('tags')
    form = AddFileForm(tags_list=tags_list)
    workflow = get_workflow(ICommunityFile, 'security', context)

    if workflow is None:
        security_states = []
    else:
        security_states = get_security_states(workflow, None, request)

    if security_states:
        form.add_field('security_state', security_state_field)

    if 'form.cancel' in request.POST:
        return HTTPFound(location=model_url(context, request))

    if 'form.submitted' in request.POST:
        try:
            converted = form.validate(request.POST)

            creator = authenticated_userid(request)

            fieldstorage = request.params.get('file')
            if not hasattr(fieldstorage, 'filename'):
                raise CustomInvalid({
                    'file': 'You must upload a file.',
                    })
            stream = fieldstorage.file
            file = create_content(ICommunityFile,
                                  title=converted['title'],
                                  stream=stream,
                                  mimetype=get_upload_mimetype(fieldstorage),
                                  filename=fieldstorage.filename,
                                  creator=creator,
                                  )
            check_upload_size(context, file, 'file')

            # For file objects, OSI's policy is to store the upload file's
            # filename as the objectid, instead of basing __name__ on the
            # title field).
            filename = basename_of_filepath(fieldstorage.filename)
            file.filename = filename
            name = make_name(context, filename, raise_error=False)
            if not name:
                msg = 'The filename must not be empty'
                raise CustomInvalid({'file': msg})
            # Is there a key in context with that filename?
            if name in context:
                msg = 'Filename %s already exists in this folder' % filename
                raise CustomInvalid({'file': msg})
            context[name] = file

            if workflow is not None:
                workflow.initialize(file)
                if 'security_state' in converted:
                    workflow.transition_to_state(file, request,
                                                 converted['security_state'])

            # Tags, attachments, alerts
            set_tags(file, request, converted['tags'])
            if converted['sendalert']:
                alerts = queryUtility(IAlerts, default=Alerts())
                alerts.emit(file, request)

            location = model_url(file, request)
            return HTTPFound(location=location)

        except Invalid, e:
            fielderrors = e.error_dict
            fill_values = form.convert(request.POST)
            tags_field = dict(
                records = [dict(tag=t) for t in request.POST.getall('tags')]
                )

    else:
        fielderrors = {}
        if workflow is None:
            security_state = ''
        else:
            security_state = workflow.initial_state
        fill_values = dict(security_state=security_state)
        tags_field = dict(records=[])

    # Render the form and shove some default values in
    page_title = 'Add File'
    api = TemplateAPI(context, request, page_title)

    # Get a little policy.  Should we suppress alerts?
    show_sendalert = queryMultiAdapter((context, request), IShowSendalert)
    if show_sendalert is not None:
        show_sendalert_field = show_sendalert.show_sendalert
    else:
        show_sendalert_field = True

    # Get a layout
    layout_provider = get_layout_provider(context, request)
    layout = layout_provider('community')

    return render_form_to_response(
        'templates/add_file.pt',
        form,
        fill_values,
        head_data=convert_to_script(dict(
                tags_field = tags_field,
                )),
        post_url=request.url,
        formfields=api.formfields,
        fielderrors=fielderrors,
        api=api,
        show_sendalert_field=show_sendalert_field,
        layout=layout,
        security_states=security_states,
        )


def show_file_view(context, request):

    page_title = context.title
    api = TemplateAPI(context, request, page_title)

    client_json_data = dict(
        tagbox = get_tags_client_data(context, request),
        )

    actions = []
    if has_permission('create', context, request):
        actions.append(
            ('Edit', 'edit.html'),
            )
        actions.append(
            ('Delete', 'delete.html'),
            )

    # If we are in an attachments folder, the backto skips the
    # attachments folder and goes up to the grandparent
    from karl.models.interfaces import IAttachmentsFolder
    from repoze.bfg.traversal import find_interface
    attachments = find_interface(context, IAttachmentsFolder)
    if attachments is not None:
        up_to = context.__parent__.__parent__
    else:
        up_to = context.__parent__
    backto = {
        'href': model_url(up_to, request),
        'title': up_to.title,
        }

    fileinfo = getMultiAdapter((context, request), IFileInfo)
    previous, next = get_previous_next(context, request)

    # Get a layout
    layout_provider = get_layout_provider(context, request)
    layout = layout_provider('community')

    return render_template_to_response(
        'templates/show_file.pt',
        api=api,
        actions=actions,
        fileinfo=fileinfo,
        head_data=convert_to_script(client_json_data),
        backto=backto,
        previous=previous,
        next=next,
        layout=layout,
        )

def download_file_view(context, request):
    f = context.blobfile.open()
    headers = [
# Let's not send content-disposition, otherwise you can't use
# image-ish Files in, say, wiki pages.
#        ('Content-Disposition', 'attachment; filename=%s' % context.filename),
        ('Content-Type', context.mimetype),
        ]

    response = Response(headerlist=headers, app_iter=f)
    return response

def edit_folder_view(context, request):
    tags_list = request.POST.getall('tags')
    form = EditFolderForm(tags_list=tags_list)
    workflow = get_workflow(ICommunityFolder, 'security', context)

    if workflow is None:
        security_states = []
    else:
        security_states = get_security_states(workflow, context, request)

    if security_states:
        form.add_field('security_state', security_state_field)

    if 'form.cancel' in request.POST:
        return HTTPFound(location=model_url(context, request))

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

            # Tags, attachments, alerts
            set_tags(context, request, converted['tags'])

            # modified
            context.modified_by = authenticated_userid(request)
            objectEventNotify(ObjectModifiedEvent(context))

            location = model_url(context, request)
            msg = '?status_message=Folder%20changed'
            return HTTPFound(location=location+msg)

        except Invalid, e:
            fielderrors = e.error_dict
            fill_values = form.convert(request.POST)
    else:
        fielderrors = {}
        if workflow is None:
            security_state = ''
        else:
            security_state = workflow.state_of(context)
        fill_values = dict(title=context.title,
                           security_state=security_state,
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
    layout = layout_provider('community')

    return render_form_to_response(
        'templates/edit_folder.pt',
        form,
        fill_values,
        head_data=convert_to_script(client_json_data),
        post_url=request.url,
        formfields=api.formfields,
        fielderrors=fielderrors,
        api=api,
        layout=layout,
        security_states = security_states,
        )


def edit_file_view(context, request):
    tags_list = request.POST.getall('tags')
    form = EditFileForm(tags_list=tags_list)
    workflow = get_workflow(ICommunityFile, 'security', context)

    if workflow is None:
        security_states = []
    else:
        security_states = get_security_states(workflow, context, request)

    if security_states:
        form.add_field('security_state', security_state_field)

    if 'form.cancel' in request.POST:
        return HTTPFound(location=model_url(context, request))

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

            fieldstorage = request.params.get('file', None)
            if hasattr(fieldstorage, 'filename'):
                context.upload(fieldstorage.file)
                context.mimetype = get_upload_mimetype(fieldstorage)
                context.filename = fieldstorage.filename
                check_upload_size(context, context, 'file')

            # Tags, attachments, alerts
            set_tags(context, request, converted['tags'])

            # modified
            context.modified_by = authenticated_userid(request)
            objectEventNotify(ObjectModifiedEvent(context))

            location = model_url(context, request)
            msg = '?status_message=File%20changed'
            return HTTPFound(location=location+msg)

        except Invalid, e:
            fielderrors = e.error_dict
            fill_values = form.convert(request.POST)
    else:
        fielderrors = {}
        if workflow is None:
            security_state = ''
        else:
            security_state = workflow.state_of(context)
        fill_values = dict(title=context.title,
                           security_state=security_state)

   # prepare client data
    client_json_data = dict(
        tags_field = get_tags_client_data(context, request),
        )

    # Render the form and shove some default values in
    page_title = 'Edit ' + context.title
    api = TemplateAPI(context, request, page_title)

    # Get a layout
    layout_provider = get_layout_provider(context, request)
    layout = layout_provider('community')

    return render_form_to_response(
        'templates/edit_file.pt',
        form,
        fill_values,
        head_data=convert_to_script(client_json_data),
        post_url=request.url,
        formfields=api.formfields,
        fielderrors=fielderrors,
        api=api,
        layout=layout,
        security_states = security_states,
        )

class AddFileForm(FormSchema):
    ignore_key_missing = True
    title = baseforms.title
    tags = baseforms.tags
    sendalert = baseforms.sendalert

class EditFileForm(FormSchema):
    title = baseforms.title
    tags = baseforms.tags

class AddFolderForm(FormSchema):
    title = baseforms.title
    tags = baseforms.tags

class EditFolderForm(FormSchema):
    title = baseforms.title
    tags = baseforms.tags

grid_folder_columns = [
    {"id": "mimetype", "label": "Type", "width": 64},
    {"id": "title", "label": "Title", "width": 666 - (64 + 128)},
    {"id": "modified_date", "label": "Last Modified", "width": 128},
]

def jquery_grid_folder_view(context, request):

    start = request.params.get('start', '0')
    limit = request.params.get('limit', '10')
    sort_on = request.params.get('sortColumn', 'modified_date')
    reverse = request.params.get('sortDirection') == 'desc'

    payload = get_filegrid_client_data(context, request,
        start = int(start),
        limit = int(limit),
        sort_on = sort_on,
        reverse = reverse,
        )

    result = JSONEncoder().encode(payload)
    return Response(result, content_type="application/x-json")


def get_filegrid_client_data(context, request, start, limit, sort_on, reverse):
    """
    Gets the client data for the file grid.

    When used, the data needs to be injected to the templates::

        head_data=convert_to_script(dict(
            filegrid = get_filegrid_client_data(context, request,
                        start = 0,
                        limit = 10,
                        sort_on = 'modified_date',
                        reverse = False,
                        ),
            tags_field = get_tags_client_data(context, request),
            # ... data for more widgets
            # ...
            ))

    Or, returned to client in case of an ajax request.
    """

    api = TemplateAPI(context, request, 'any_title')

    ##columns = request.params.get('columns', '').capitalize() == 'True'

    # Now get the data that goes with this, then adapt into FileInfo
    info = get_container_batch(context, request,
        batch_start=start,
        batch_size=limit,
        sort_index=sort_on,
        reverse=reverse,
        )
    entries = [getMultiAdapter((item, request), IFileInfo)
        for item in info['entries']]

    records = []
    for entry in entries:
        records.append([
            '<img src="%s/images/%s" alt="icon" title="%s"/>' % (
                api.static_url,
                entry.mimeinfo['small_icon_name'],
                entry.mimeinfo['title'],
                ),
            '%s<a href="%s" style="display: none;"/>' % (
                entry.title,
                entry.url,
                ),
            entry.modified,
            ])

    payload = dict(
        columns = grid_folder_columns,
        records = records,
        totalRecords = info['total'],
        sortColumn = sort_on,
        sortDirection = reverse and 'desc' or 'asc',
    )

    return payload


def get_upload_mimetype(fieldstorage):
    res = fieldstorage.type
    if res in (
            'application/x-download',
            'application/x-application',
            'application/binary',
            'application/octet-stream',
            ):
        # The browser sent a meaningless file type.  Firefox on Ubuntu
        # does this to some people:
        #  https://bugs.launchpad.net/ubuntu/+source/firefox-3.0/+bug/84880
        # Try to guess a more sensible mime type from the filename.
        guessed_type, _ = mimetypes.guess_type(fieldstorage.filename)
        if guessed_type:
            res = guessed_type
    return res

