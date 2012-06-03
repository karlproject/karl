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

from zope.component import getMultiAdapter
from zope.component import ComponentLookupError

from pyramid.renderers import render
from pyramid.renderers import render_to_response

from pyramid.traversal import find_resource

from karl.utils import find_intranets
from karl.views.api import TemplateAPI

from karl.views.interfaces import IIntranetPortlet


def retail_view(context, request):

    layout = request.layout_manager.layout
    layout.section_style = 'header'
    page_title = context.title
    api = TemplateAPI(context, request, page_title)

    middle_portlet_html = _get_portlet_html(context, request,
                                            context.middle_portlets)
    right_portlet_html = _get_portlet_html(context, request,
                                           context.right_portlets)
    current_intranet = api.current_intranet
    feature = getattr(find_intranets(current_intranet), 'feature', u'')

    # Rendering this separately gives us a chance later to think about
    # some kind of caching.
    body = render(
        'templates/intranethome_body.pt',
        dict(current_intranet=current_intranet,
             feature=feature,
             middle_portlet_html=middle_portlet_html,
             right_portlet_html=right_portlet_html),
        request=request
        )

    return render_to_response(
        'templates/intranet_homepage.pt',
        dict(api=api, body=body),
        request=request,
        )

def _get_portlet_html(context, request, portlet_ids):
    missing = '<div class="generic-portlet"><p>Missing portlet at %s</p></div>'
    notaportlet = '<div class="sections"><p>%s is not a portlet</p></div>'
    html = ''
    for portlet_id in portlet_ids:
        try:
            model = find_resource(context, portlet_id)
        except KeyError:
            html += missing % portlet_id
            continue
        try:
            portlet_info = getMultiAdapter((model, request), IIntranetPortlet)
        except ComponentLookupError:
            html += notaportlet % portlet_id
            continue
        html += portlet_info.asHTML

    return html
