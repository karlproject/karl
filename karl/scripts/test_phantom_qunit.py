
import sys
import os
import subprocess

def _concat_path(fname, *rnames):
    return os.path.join(os.path.dirname(fname), *rnames)

def module_path(mod, *rnames):
    return _concat_path(mod.__file__, *rnames)

def run_phantom(config_file, resource_url, verbose=False):
    attrs = ('phantomjs', config_file, resource_url)
    if verbose:
        attrs += ('-v', )
    status = subprocess.call(attrs)
    return (status == 0)

def main(argv=sys.argv):
    import karl.phantom_qunit
    config_file = module_path(karl.phantom_qunit, 'phantom-qunit.js')
    if len(argv) !=1:
        raise RuntimeError, 'Usage: test_phantom_qunit'
    verbose = False
    prefix = 'http://127.0.0.1:6543/pg'

    r = 'r1332503085/'    # XXX This, of course, cannot work.

    tests = [
        prefix + '/popper-static/popper-plugins/popper-example/tests/test.html',
        prefix + '/popper-static/popper-plugins/popper-tagbox/tests/test.html',
        prefix + '/popper-static/popper-plugins/popper-pushdown/tests/test.html',

        # XXX broken because of static path
        #prefix2 + '/static' + r + '/karl-plugins/karl-contentfeeds/test.html',

        prefix + '/static' + r + '/tinymce/3.3.9.2/plugins/paste/tests/test.html',

        # XXX broken still
        #prefix + '/static' + r + '/tinymce/3.3.9.2/plugins/imagedrawer/tests/test.html',

        prefix + '/static' + r + '/tinymce/3.3.9.2/plugins/imagedrawer/tests/test_notiny.html',

        #prefix + '/static/tinymce/3.3.9.2/plugins/kaltura/tests/test.html',
        #prefix + '/static/tinymce/3.3.9.2/plugins/spellchecker/tests/test.html',
        #prefix + '/static/tinymce/3.3.9.2/plugins/wicked/tests/test.html',
        #prefix + '/static/tinymce/3.3.9.2/themes/advanced/skins/karl/tests/test.html',
    ]

    failures = False
    for resource_url in tests:
        success = run_phantom(config_file, resource_url, verbose=verbose)
        failures = failures or not success

    if failures:
        raise SystemExit, 'Some tests failed'


if __name__ == '__main__':
    main()
