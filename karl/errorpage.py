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

from traceback import format_exc

from webob import Request

from repoze.bfg.chameleon_zpt import render_template_to_response

GENERAL_MESSAGE = """
%(system_name)s encountered an application error.  Please click
the link below to return to the %(system_name)s home page.
"""
NOTFOUND_MESSAGE = """
%(system_name)s was unable to find the content at this URL."""

class ErrorPageFilter(object):
    """ Simple middleware to provide pretty error pages """

    def __init__(self, app, global_config,
                 static_url, home_url, errorlog_url=None,
                 system_name='KARL'):
        self.app = app
        self._static_url = static_url
        self._home_url = home_url
        self._errorlog_url = errorlog_url
        self._system_name = system_name

    def __call__(self, environ, start_response):

        req = Request(environ)
        try:
            resp = req.get_response(self.app)
        except:
            # General failures get wrapped into a General KARL Error
            static_url = req.relative_url(self._static_url, to_application=True)
            home_url = req.relative_url(self._home_url, to_application=True)
            if self._errorlog_url is None:
                errorlog_url = None
            else:
                errorlog_url = req.relative_url(
                    self._errorlog_url, to_application=True
                )

            traceback_info = format_exc()
            resp = render_template_to_response(
                'karl.views:templates/wsgi_errormsg.pt',
                error_message='General Error',
                error_text=GENERAL_MESSAGE,
                static_url=static_url,
                errorlog_url=errorlog_url,
                home_url=home_url,
                traceback_info=traceback_info,
                )
            resp.status = 500
            return resp(environ, start_response)

        status = resp.status_int
        if status in (404, 500):
            static_url = req.relative_url(self._static_url, to_application=True)
            home_url = req.relative_url(self._home_url, to_application=True)
            if self._errorlog_url is None:
                errorlog_url = None
            else:
                errorlog_url = req.relative_url(
                    self._errorlog_url, to_application=True
                )
            error_text = NOTFOUND_MESSAGE if status == 404 else GENERAL_MESSAGE
            error_text %= {'system_name': self._system_name}
            resp = render_template_to_response(
                'karl.views:templates/wsgi_errormsg.pt',
                error_message='Not Found',
                static_url=static_url,
                error_text=error_text,
                home_url=home_url,
                errorlog_url=errorlog_url,
                traceback_info=None,
                )
            resp.status = status
            return resp(environ, start_response)

        return resp(environ, start_response)

