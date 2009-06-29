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
"""Support code for Karl scripts
"""

import os
import sys
from paste.deploy import loadapp
from repoze.bfg.scripting import get_root

def get_default_config():
    """Get the default configuration file name.

    This should be called by a console script. We assume that the
    console script lives in the 'bin' dir of a sandbox or buildout, and
    that the karl.ini file lives in the 'etc' directory of the sandbox
    or buildout.
    """
    me = sys.argv[0]
    me = os.path.abspath(me)
    sandbox = os.path.dirname(os.path.dirname(me))
    config = os.path.join(sandbox, 'etc', 'karl.ini')
    return os.path.abspath(os.path.normpath(config))

def open_root(config, name='karl'):
    """Open the database root object, given a Paste Deploy config file name.

    Returns (root, closer).  Call the closer function to close the database
    connection.
    """
    config = os.path.abspath(os.path.normpath(config))
    app = loadapp('config:%s' % config, name=name)
    return get_root(app)
