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


# Simple deployment-oriented middleware to format errors to look like
# KARL pages

import logging
from traceback import format_exc
from ZODB.POSException import ReadOnlyError

from pyramid.exceptions import NotFound
from pyramid.httpexceptions import HTTPNotFound

GENERAL_MESSAGE = """
%(system_name)s encountered an application error.  Please click
the link below to return to the %(system_name)s home page.
"""

NOTFOUND_MESSAGE = """
%(system_name)s was unable to find the content at this URL."""

READONLY_MESSAGE = """ %(system_name)s has been placed in read only mode
temporarily so that administrators may perform routine maintenance tasks.
During this time no new content may be added to %(system_name)s or any edits
made. Please try again later. Thank you."""


def errorpage(context, request):
    system_name = request.registry.settings.get('system_name', 'KARL')

    if _matches(context, ReadOnlyError):
        error_message = 'Site is in Read Only Mode'
        error_text = READONLY_MESSAGE % {'system_name': system_name}
        traceback_info = None
        request.response.status_int = 500

    elif _matches(context, NotFound, HTTPNotFound):
        error_message = 'Not Found'
        error_text = NOTFOUND_MESSAGE % {'system_name': system_name}
        traceback_info = None
        request.response.status_int = 404

    else:
        error_message = 'General Error'
        error_text = GENERAL_MESSAGE % {'system_name': system_name}
        traceback_info = unicode(format_exc(), 'UTF-8')
        request.response.status_int = 500

        # Log the error
        message = ['%s: %s' % (type(context).__name__, str(context))]
        message.append('Exception when processing %s' % request.url)
        message.append('Referer: %s' % request.referer)
        logging.getLogger('karl').error('\n'.join(message), exc_info=True)
    
    request.layout_manager.use_layout('anonymous')

    return {
        'error_message': error_message,
        'error_text': error_text,
        'traceback_info': traceback_info}


def _matches(e, *types):
    for t in types:
        if e is t or isinstance(e, t):
            return True
    return False
