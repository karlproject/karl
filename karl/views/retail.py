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

from repoze.bfg.chameleon_zpt import render_template
from repoze.bfg.chameleon_zpt import render_template_to_response

from repoze.bfg.traversal import find_model

from karl.utils import find_intranets
from karl.views.api import TemplateAPI

from karl.views.interfaces import IIntranetPortlet


def retail_view(context, request):

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
    body = render_template(
        'templates/intranethome_body.pt',
        current_intranet=current_intranet,
        feature=feature,
        middle_portlet_html=middle_portlet_html,
        right_portlet_html=right_portlet_html,
        )

    return render_template_to_response(
        'templates/intranet_homepage.pt',
        api=api,
        body=body,
        )

def _get_portlet_html(context, request, portlet_ids):
    missing = '<div class="sections"><p>Missing portlet at %s</p></div>'
    html = ''
    for portlet_id in portlet_ids:
        try:
            model = find_model(context, portlet_id)
        except KeyError:
            html += missing % portlet_id
            continue
        portlet_info = getMultiAdapter((model, request), IIntranetPortlet)
        html += portlet_info.asHTML

    return html
