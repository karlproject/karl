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

"""Views registered to multiple content types"""

from zope.component import getMultiAdapter
from webob.exc import HTTPFound

from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.url import model_url

from karl.views.interfaces import ILayoutProvider

from karl.views.api import TemplateAPI
from repoze.folder.interfaces import IFolder

def delete_resource_view(context, request):

    page_title = 'Delete ' + context.title
    api = TemplateAPI(context, request, page_title)

    confirm = request.params.get('confirm')
    if confirm:
        location = model_url(
            context.__parent__, request,
            query=dict(status_message= 'Deleted %s' % context.title)
            )
        del context.__parent__[context.__name__]
        return HTTPFound(location=location)

    # Get a layout
    layout_provider = getMultiAdapter((context, request), ILayoutProvider)
    layout = layout_provider('community')

    # LP #399337, Add warning on delete of Folder with content inside
    num_children = 0
    if IFolder.providedBy(context):
        num_children = len(context)

    return render_template_to_response(
        'templates/delete_resource.pt',
        api=api,
        layout=layout,
        num_children=num_children,
        )

