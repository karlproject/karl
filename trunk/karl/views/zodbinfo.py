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

import time
from repoze.bfg.chameleon_zpt import render_template_to_response

class ConnectionInfo:

    def __init__(self, conn):
        self.connection = conn
        opened = conn._opened
        if opened:
            self.opened = time.ctime(opened)
        else:
            self.opened = '-'
        self.ngsize = conn._cache.cache_non_ghost_count
        self.size = len(conn._cache)

def show_zodbinfo(context, request):
    databases = context._p_jar.db().databases.items()
    databases.sort()
    dbinfo = []
    for database_name, database in databases:
        connections = []
        def add_conn(conn):
            connections.append((id(conn), ConnectionInfo(conn)))
        database._connectionMap(add_conn)
        connections.sort()
        connections = [c[1] for c in connections]
        dbinfo.append({
            'name': database_name,
            'connections': connections,
            })
    return render_template_to_response(
        'templates/zodbinfo.pt',
        dbinfo=dbinfo)
