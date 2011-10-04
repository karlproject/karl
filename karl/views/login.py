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

from datetime import datetime
from urllib import urlencode
from urlparse import urljoin

from pyramid.renderers import render_to_response
from pyramid.url import resource_url
from pyramid.httpexceptions import HTTPFound

from karl.utils import find_profiles
from karl.utils import find_site
from karl.utils import get_setting

from karl.views.api import TemplateAPI

def _fixup_came_from(request, came_from):
    if came_from is None:
        return request.application_url
    came_from = urljoin(request.application_url, came_from)
    if came_from.endswith('login.html'):
        came_from = came_from[:-len('login.html')]
    elif came_from.endswith('logout.html'):
        came_from = came_from[:-len('logout.html')]
    return came_from

def login_view(context, request):

    plugins = request.environ.get('repoze.who.plugins', {})
    auth_tkt = plugins.get('auth_tkt')

    came_from = _fixup_came_from(request, request.POST.get('came_from'))

    if request.params.get('form.submitted', None) is not None:

        challenge_qs = {'came_from': came_from}
        # identify
        login = request.POST.get('login')
        password = request.POST.get('password')
        if login is None or password is None:
            return HTTPFound(location='%s/login.html'
                                        % request.application_url)
        credentials = {'login': login, 'password': password}
        max_age = request.POST.get('max_age')
        if max_age is not None:
            credentials['max_age'] = int(max_age)

        # authenticate
        authenticators = filter(None,
                                [plugins.get(name)
                                   for name in ['zodb', 'zodb_impersonate']])
        userid = None
        if authenticators:
            reason = 'Bad username or password'
        else:
            reason = 'No authenticatable users'

        for plugin in authenticators:
            userid = plugin.authenticate(request.environ, credentials)
            if userid:
                break

        # if not successful, try again
        if not userid:
            challenge_qs['reason'] = reason
            return HTTPFound(location='%s/login.html?%s'
                             % (request.application_url,
                                urlencode(challenge_qs, doseq=True)))

        # else, remember
        credentials['repoze.who.userid'] = userid
        if auth_tkt is not None:
            remember_headers = auth_tkt.remember(request.environ, credentials)
        else:
            remember_headers = []

        # log the time on the user's profile, unless in read only mode
        read_only = get_setting(context, 'read_only', False)
        if not read_only:
            profiles = find_profiles(context)
            if profiles is not None:
                profile = profiles.get(userid)
                if profile is not None:
                    profile.last_login_time = datetime.utcnow()

        # and redirect
        return HTTPFound(headers=remember_headers, location=came_from)

    page_title = '' # Per #366377, don't say what screen
    api = TemplateAPI(context, request, page_title)

    came_from = _fixup_came_from(request,
                                 request.params.get('came_from', request.url))

    api.status_message = request.params.get('reason', None)
    response = render_to_response(
        'templates/login.pt',
        dict(api=api,
             came_from=came_from,
             nothing='',
             app_url=request.application_url),
        request=request,
        )
    if auth_tkt is not None:
        forget_headers = auth_tkt.forget(request.environ, {})
        response.headers.update(forget_headers)
    return response

def logout_view(context, request, reason='Logged out'):
    site = find_site(context)
    site_url = resource_url(site, request)
    login_url = resource_url(site, request, 'login.html', query={
        'reason': reason, 'came_from': site_url})

    redirect = HTTPFound(location=login_url)
    plugins = request.environ.get('repoze.who.plugins', {})
    auth_tkt = plugins.get('auth_tkt')
    if auth_tkt is not None:
        forget_headers = auth_tkt.forget(request.environ, {})
        redirect.headers.update(forget_headers)
    return redirect


