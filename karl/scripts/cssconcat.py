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
    tinymce_base_dir = os.path.join(static_dir, 'tinymce')
    tinymce_dir = os.path.join(tinymce_base_dir, '3.3.9.2')

    skin_dir = os.path.join(tinymce_dir, 'themes', 'advanced', 'skins', 'karl')

    # tinymce packed css
    # It must be in the skin directory, because it traverses resources from there.
    karl_tiny_css = os.path.join(skin_dir, 'karl-tiny-packed.css')
    f = file(karl_tiny_css, 'w')
    for fname in itertools.chain(
            filesindir(tinymce_dir, 'themes/advanced/skins/karl/ui.css'),
            filesindir(tinymce_dir, 'plugins/imagedrawer/css/ui.css'),
            ):
        f.write(file(fname).read())
    f.close()
    print "Successfully produced resource", karl_tiny_css

if __name__ == '__main__':
    main()
