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
from repoze.bfg.url import model_url

from karl.views.api import TemplateAPI

def redirect_up_view(context, request):
    location = model_url(context.__parent__, request)
    return HTTPFound(location=location)

def redirect_favicon(context, request):
    api = TemplateAPI(context, request)
    location = '%s/favicon.ico' % api.static_url
    return HTTPFound(location=location)

def redirect_rss_view_xml(context, request):
    location = model_url(context, request, 'atom.xml')
    return HTTPFound(location=location)
