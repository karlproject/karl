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

# Simple middleware to measure elapsed time and inject into the
# response HTML.

from webob import Request

import time

class TimeitFilter(object):
    """Simple middleware to inject time measurement into response"""

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        """Dispatcher to processBefore, processAfter, no-op, etc."""

        req = Request(environ)

        # Mark the start time
        start = time.time()

        # Generate the response.  If text/html, print elapsed
        resp = req.get_response(self.app)
        if resp.content_type == "text/html":
            elapsed = str(1 / (time.time() - start))[0:5]
            first_result = resp.body
            before = 'id="header-user-menu">'
            scoreboard = """
<div style="float:left">Requests per second: %s</div>
"""
            after = before + scoreboard % elapsed
            resp.body = first_result.replace(before, after, 1)

        return resp(environ, start_response)

def main(app, global_conf, **local_conf):
    """Middleware to inject elapsed time into a web page"""

    return TimeitFilter(app)


