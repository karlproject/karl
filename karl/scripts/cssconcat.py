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

""" Concatenate the css resources  

This is at the moment only used for creating a concatenated
theme css for the jquery.ui theme.
The jquery ui builder process would also be usable to
create this css.

This script only needs to be used if some component is added
to jquery.ui in addition to the one we currently use.
"""

import sys
import os
import karl.views
import itertools

def _concat_path(fname, *rnames):
    return os.path.join(os.path.dirname(fname), *rnames)

def module_path(mod, *rnames):
    return _concat_path(mod.__file__, *rnames)

def filesindir(dir, *filenames):
    return (os.path.join(dir, f) for f in filenames)

def main(argv=sys.argv):
    if len(argv) > 1:
        raise RuntimeError, 'cssconcat accepts no parameters.'
    static_dir = module_path(karl.views, 'static')

    ui_dir = os.path.join(static_dir, 'jquery-ui', '1.7')
    theme_dir = os.path.join(ui_dir, 'themes', 'base')

    theme_css = os.path.join(theme_dir, 'jquery-ui-1.7.2.karl.css')
    f = file(theme_css, 'w')
    for fname in itertools.chain(
            filesindir(theme_dir, 'ui.core.css'),
            # selected components come here
            filesindir(theme_dir, 'ui.datepicker.css'),
            filesindir(theme_dir, 'ui.dialog.css'),
            #
            filesindir(theme_dir, 'ui.theme.css'),
            ):
        f.write(file(fname).read())
    f.close()
    print "Successfully produced resource", theme_css

if __name__ == '__main__':
    main()
