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

from webob.exc import HTTPUnauthorized

from repoze.bfg.chameleon_zpt import render_template_to_response
from karl.views.api import TemplateAPI
from karl.utils import get_setting

def login_view(context, request):

    system_name = get_setting(context, 'system_name')

    page_title = '' # Per #366377, don't say what screen
    api = TemplateAPI(context, request, page_title)

    came_from = request.params.get('came_from', request.url)

    if came_from.endswith('login.html'):
        came_from = came_from[:-len('login.html')]
    elif came_from.endswith('logout.html'):
        came_from = came_from[:-len('logout.html')]

    api.status_message = status_message=request.params.get('reason', None)
    response = render_template_to_response(
        'templates/login.pt',
        api=api,
        came_from=came_from,
        nothing='',
        app_url=request.application_url,
        )
    plugins = request.environ.get('repoze.who.plugins', {})
    auth_tkt = plugins.get('auth_tkt')
    if auth_tkt is not None:
        forget_headers = auth_tkt.forget(request.environ, {})
        response.headers.update(forget_headers)
    return response

def logout_view(context, request):
    unauthorized = HTTPUnauthorized()
    unauthorized.headerlist.append(
        ('X-Authorization-Failure-Reason', 'Logged out'))
    return unauthorized


