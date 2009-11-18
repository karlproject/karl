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

""" GenerateStats


"""

from karl.scripting import get_default_config
from karl.scripting import open_root
from optparse import OptionParser
import os
import sys
import transaction
from karl.models.interfaces import ICommunity
from repoze.bfg.traversal import find_model
from karl.utils import find_communities
from datetime import datetime
import time

def getCommCount(root):
    communitycoun = find_communities(root)
    communitycount = len(communitycoun)
    return communitycoun

def main():
    parser = OptionParser(description=__doc__,
                          usage='usage: %prog [options] username password')
    parser.add_option('-C', '--config', dest='config', default=None,
        help="Specify a paster config file. Defaults to $CWD/etc/karl.ini")

    options, args = parser.parse_args()

    config = options.config
    if config is None:
        config = get_default_config()
    root, closer = open_root(config)
    thiscount =  len(getCommCount(root))
    me = sys.argv[0]
    me = os.path.abspath(me)
    sandbox = os.path.dirname(os.path.dirname(me))
    dirname = sandbox + '/var/stats/'
    if not os.path.isdir(dirname):
        os.mkdir(dirname)
    outfile_path = os.path.join(dirname, 'stats.csv')
    oline = str(datetime.fromtimestamp(time.time()).strftime("%m/%d/%y %H:%M"))+","+str(thiscount)+'\n'
    f = open(outfile_path, 'a')
    f.write(oline)
    f.close()

if __name__ == '__main__':
    main()