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

"""Publish static resources under /static/"""

import os

from webob.exc import HTTPFound

from repoze.bfg.url import model_url
from repoze.bfg.view import static

from karl.views.utils import get_user_home

##from karl.models.interfaces import IFiles
##from karl.models.interfaces import IOthers

here = os.path.abspath(os.path.dirname(__file__))

static_view = static('static')

def site_view(context, request):
    home, extra_path = get_user_home(context, request)
    return HTTPFound(location=model_url(home, request, *extra_path))
