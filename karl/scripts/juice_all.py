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

""" Concatenate the javascript resources  """

import sys
import os
import karl.views
import subprocess

def _concat_path(fname, *rnames):
    return os.path.join(os.path.dirname(fname), *rnames)

def module_path(mod, *rnames):
    return _concat_path(mod.__file__, *rnames)

def run_juicer(resource, output="min/"):
    attrs = ('juicer', 'merge', '-i', '--force', 
        '-o', os.path.join(os.path.dirname(resource), output), resource)
    print '##### Will run: ' + ' '.join(attrs) 
    status = subprocess.call(attrs)
    if status != 0:
        print "\n\n##### ERROR: FAILED compression of " + resource
        print '\nTry to consolidate problems by running manually:\n\n' + ' '.join(attrs) + '\n'
        raise SystemExit, "Compression of " + resource + " failed"

def main(argv=sys.argv):
    if len(argv) > 1:
        raise RuntimeError, 'juice_all accepts no parameters.'
    static_dir = module_path(karl.views, 'static')
    tinymce_dir = module_path(karl.views, 'static', 'tinymce')

    run_juicer(os.path.join(static_dir, 'karl-ui.js')) 
    run_juicer(os.path.join(static_dir, 'karl-ui.css'))  

    run_juicer(os.path.join(static_dir, 'karl-multifileupload.js')) 
    run_juicer(os.path.join(static_dir, 'karl-multifileupload.css'))  

    run_juicer(os.path.join(tinymce_dir, 'tinymce-3.5.2.karl.js')) 
    run_juicer(os.path.join(tinymce_dir, 'tinymce-3.5.2.karl.css')) 

    run_juicer(os.path.join(static_dir, 'karl-wikitoc.js')) 
    run_juicer(os.path.join(static_dir, 'karl-wikitoc.css'))  

    # Resources for ux2

    ux2_dir = module_path(karl.views, 'static', 'ux2', 'js')
    ux2_min_dir = module_path(karl.views, 'static', 'ux2', 'min')

    run_juicer(os.path.join(ux2_dir, 'karl-ux2-head.js'),
        output=ux2_min_dir)
    run_juicer(os.path.join(ux2_dir, 'karl-ux2-core.js'),
        output=ux2_min_dir)
    run_juicer(os.path.join(ux2_dir, 'karl-ux2-legacy.js'),
        output=ux2_min_dir)
    run_juicer(os.path.join(ux2_dir, 'karl-ux2-slickgrid.js'),
        output=ux2_min_dir)
    run_juicer(os.path.join(ux2_dir, 'karl-ux2-multiupload.js'),
        output=ux2_min_dir)

    run_juicer(os.path.join(tinymce_dir, 'karl-ux2-tinymce.js'))
    run_juicer(os.path.join(tinymce_dir, 'karl-ux2-tinymce.css'))
    run_juicer(os.path.join(tinymce_dir, 'tinymce-popup-utils.js'))

    print "\n\n##### All files compressed OK"


if __name__ == '__main__':
    main()
