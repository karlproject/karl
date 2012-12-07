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

import unittest


class TimeitMiddlewareTests(unittest.TestCase):

    def _getTargetClass(self):
        from karl.timeit import TimeitFilter
        return TimeitFilter

    def _makeOne(self, app=None):
        if app is None:
            app = DummyApp()
        return self._getTargetClass()(app)

    def _makeEnviron(self, **kw):
        environ = {'REQUEST_METHOD': 'GET'}
        environ.update(kw)
        return environ

    def _startResponse(self, status, headers):
        self._started = (status, headers)

    def test_response_not_HTML(self):
        app = DummyApp(headers=[('Content-Type', 'text/plain')], body='xxx')
        mw = self._makeOne(app)
        environ = self._makeEnviron()
        app_iter = mw(environ, self._startResponse)
        self.assertEqual(list(app_iter), ['xxx'])
        self.assertEqual(self._started[0], '200 OK')
        self.assertEqual(self._started[1], [('Content-Type', 'text/plain')])

    def test_response_w_HTML(self):
        app = DummyApp(headers=[('Content-Type', 'text/html')],
                                body=test_html)
        mw = self._makeOne(app)
        environ = self._makeEnviron()
        app_iter = mw(environ, self._startResponse)

        body = list(app_iter)[0]
        self.assert_(match_string in body)
        self.assertEqual(self._started[0], '200 OK')
        self.failUnless(('Content-Type', 'text/html') in self._started[1])

test_html = """\
<html><body>
  <div id="header-user-menu"></div>
</body></html>
"""
match_string = '<div style="float:left">Requests per second:'

class DummyApp:

    def __init__(self, status='200 OK', headers=(), body=''):
        self.status = status
        self.headers = list(headers)
        self.body_chunks = [body]

    def __call__(self, environ, start_response):
        start_response(self.status, self.headers)
        return self.body_chunks
