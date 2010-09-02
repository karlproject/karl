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

"""addlicense [OPTIONS] dirname1 dirname2 ...

Adjusts .py files in each directory (recursively) to contain license
text at the top of the file.  For each .py file encountered as we
recurse, print the filename and whether it needed changing or not.  If
``dry-run`` is not specified, change the file in place to contain the
license text.

Options
=======

--licensefile (-l)       Path to file that contains license text.
                         Defaults to internal copy of OSI license text.

--dry-run (-d)           Don't actually change the files, just print
                         output

--help (-h -?)           Print this help.

--skip-names             comma-separated list of file or directory names to skip
                         (version control directories are skipped anyway)

"""

import os
import sys
import getopt


def usage(self, message=None, rc=1):
    print __doc__
    if message is not None:
        print message
        print
    sys.exit(rc)

def main(argv=sys.argv):
    name, argv = argv[0], argv[1:]

    try:
        opts, args = getopt.getopt(argv, 'l:dh?',
                                         ['licensefile=',
                                          'skip-names=',
                                          'dry-run',
                                          'help',
                                         ])
    except getopt.GetoptError, e:
        usage(e)
        
    config = None
    dry_run = False
    license = OSI_LICENSE

    skip_names = [
        'ez_setup.py',
        'karl/static/extjs/examples/locale/create_languages_js.py',
        'karl/converters/stripogram',
        'karl/static/kukit.js',
        'karl/docs',
        'karl.content/docs'
        ]
    
    if not len(args):
        usage('Directory names required')

    for k, v in opts:
        if k in ('-l', '--licensefile'):
            license = open(v, 'r').read()
        if k in ('-d', '--dry-run'):
            dry_run = True
        if k in ('--skip-names',):
            skip_names = [x.strip() for x in v.split(',')]
        elif k in ('-h', '-?', '--help'):
            usage(rc=2)

    for toplevel in args:
        tochange = []
        full_skipnames = []
        for skip_name in skip_names:
            if not skip_name.startswith(toplevel):
                skip_name = os.path.join(toplevel, skip_name)
            full_skipnames.append(skip_name)
        for root, dirs, files in os.walk(toplevel):
            if '.svn' in dirs:
                dirs.remove('.svn')
            if 'CVS' in dirs:
                dirs.remove('CVS')
            if '.hg' in dirs:
                dirs.remove('.hg')
            for dn in dirs:
                if os.path.join(root, dn) in full_skipnames:
                    print os.path.join(root, dn), 'SKIPDIR'
                    dirs.remove(dn)
            for fn in files:
                if os.path.splitext(fn)[1] == '.py':
                    data = ''
                    absp = os.path.join(root, fn)
                    if absp in full_skipnames:
                        print absp, 'SKIPFILE'
                        continue
                    fh = open(absp)
                    while 1:
                        firstline = fh.readline()
                        if firstline == '':
                            break
                        if firstline.strip():
                            break
                    data = firstline + fh.read()
                    if license in data:
                        print absp, 'ALREADY_DONE'
                    elif '##' in firstline:
                        if not (
                            (absp == __file__) or ('-*- coding' in firstline)):
                            raise ValueError(
                                absp + ' already has a license header')
                    else:
                        if dry_run:
                            print 'CHANGEABLE'
                        else:
                            tochange.append((absp, license + data))

        for path, data in tochange:
            f = open(path, 'w')
            f.write(data)
            f.close()
            print path, 'CHANGED'
                    
OSI_LICENSE = """\
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

"""
