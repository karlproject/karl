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

"""Reset psswords for all users or members of a group

  reset_passwords [<group>]
"""

from repoze.workflow import get_workflow
from karl.models.interfaces import IProfile
from karl.scripting import get_default_config
from karl.scripting import open_root
from karl.utils import find_profiles
from karl.utils import find_users
from optparse import OptionParser
from repoze.lemonade.content import create_content

import transaction

import random
import string

import logging


logging.basicConfig()


def reset_passwords(root, group):
    user_store = find_users(root)
    users = user_store.users_in_group(group)
    for user in users:
        password = ''.join(random.SystemRandom().choice(
            string.ascii_uppercase + string.digits)
            for _ in range(32))
        user_store.change_password(user, password)
        print "reset password for {}".format(user)


def main():
    parser = OptionParser(description=__doc__,
                          usage='usage: %prog [options]')
    parser.add_option('-C', '--config', dest='config', default=None,
        help="Specify a paster config file. Defaults to $CWD/etc/karl.ini")

    options, args = parser.parse_args()

    try:
        group = args[0]
    except IndexError:
        parser.error('need "group" arg')

    config = options.config
    if config is None:
        config = get_default_config()
    root, closer = open_root(config)

    try:
        reset_passwords(root, group)
    except:
        transaction.abort()
        raise
    else:
        transaction.commit()


if __name__ == '__main__':
    main()
