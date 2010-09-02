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

"""Add an administrative user to KARL:

  adduser <username> <password>
"""

from karl.models.interfaces import IProfile
from karl.scripting import get_default_config
from karl.scripting import open_root
from karl.utils import find_profiles
from karl.utils import find_users
from optparse import OptionParser
from repoze.lemonade.content import create_content

import transaction

def adduser(root, userid, password):
    users = find_users(root)
    if users.get_by_id(userid) is not None:
        raise ValueError("User already exists with id: %s" % userid)

    profiles = find_profiles(root)
    if userid in profiles:
        raise ValueError("Profile already exists with id: %s" % userid)

    users.add(userid, userid, password, ['group.KarlAdmin'])
    profiles[userid] = create_content(
        IProfile, firstname='System', lastname='User'
    )

def main():
    parser = OptionParser(description=__doc__,
                          usage='usage: %prog [options] username password')
    parser.add_option('-C', '--config', dest='config', default=None,
        help="Specify a paster config file. Defaults to $CWD/etc/karl.ini")

    options, args = parser.parse_args()
    try:
        username, password = args
    except ValueError:
        parser.error('Too many or too few args (need "username password"))')

    config = options.config
    if config is None:
        config = get_default_config()
    root, closer = open_root(config)

    try:
        adduser(root, username, password)
    except:
        transaction.abort()
        raise
    else:
        transaction.commit()

if __name__ == '__main__':
    main()
