
import sys
import os
import subprocess

def _concat_path(fname, *rnames):
    return os.path.join(os.path.dirname(fname), *rnames)

def module_path(mod, *rnames):
    return _concat_path(mod.__file__, *rnames)

def run_phantom(config_file, resource_url, verbose=False, xml=False):
    attrs = ('phantomjs', config_file, resource_url)
    if verbose:
        attrs += ('-v', )
    if xml:
        attrs += ('--xml', )
    status = subprocess.call(attrs)
    return (status == 0)

def main(argv=sys.argv):
    import karl.phantom_qunit
    from karl import views as karl_views # we use views, as karl is multiegg
    config_file = module_path(karl.phantom_qunit, 'phantom-qunit.js')
    verbose = False
    xml = False
    for arg in argv[1:]:
        if arg == '-v':
            verbose = True
        elif arg == '--xml':
            xml = True
        else:
            raise RuntimeError, 'Usage: test_phantom_qunit [-v] [--xml]'

    karl_static_prefix = module_path(karl_views, 'static')

    tests = [
        karl_static_prefix + '/ux2/plugins/popper-example/tests/test.html',
        karl_static_prefix + '/ux2/plugins/popper-tagbox/tests/test.html',
        karl_static_prefix + '/ux2/plugins/popper-pushdown/tests/test.html',

        karl_static_prefix + '/karl-plugins/karl-contentfeeds/test.html',
        karl_static_prefix + '/tinymce/3.3.9.2/plugins/paste/tests/test.html',

        # XXX broken still, but note they are the pre-ux2 stuff
        #karl_static_prefix + '/tinymce/3.3.9.2/plugins/imagedrawer/tests/test.html',
        #karl_static_prefix + '/tinymce/3.3.9.2/plugins/imagedrawer/tests/test_notiny.html',
        karl_static_prefix + '/tinymce/3.3.9.2/plugins/kaltura/tests/test.html',
        karl_static_prefix + '/tinymce/3.3.9.2/plugins/spellchecker/tests/test.html',
        karl_static_prefix + '/tinymce/3.3.9.2/plugins/wicked/tests/test.html',
        #karl_static_prefix + '/tinymce/3.3.9.2/themes/advanced/skins/karl/tests/test.html',

        karl_static_prefix + '/tinymce-plugins/wicked/tests/test.html',
        karl_static_prefix + '/tinymce-plugins/imagedrawer/tests/test.html',
        # XXX untestable, due to the way we load the snippet:
        #karl_static_prefix + '/tinymce-plugins/imagedrawer/tests/test_notiny.html',
    ]

    if xml:
        print '<testsuites>'

    failures = False
    for resource_url in tests:
        success = run_phantom(config_file, resource_url, verbose=verbose, xml=xml)
        failures = failures or not success

    if xml:
        print '</testsuites>'

    if failures:
        raise SystemExit, 'Some tests failed'


if __name__ == '__main__':
    main()
