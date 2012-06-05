import os
import pkg_resources
import sys
import time

from pyramid.chameleon_zpt import renderer_factory
from pyramid.exceptions import NotFound
from pyramid.renderers import RendererHelper
from pyramid.threadlocal import get_current_request

from pyramid_formish import IFormishRenderer
from pyramid_formish import ZPTRenderer as FormishZPTRenderer

import karl.ux2
from karl.utils import asbool

# Debug toolbar is disabled temporarily
##
#try:
##    import pyramid_debugtoolbar
##    pyramid_debugtoolbar  # pyflakes stfu
##except ImportError:
##    pyramid_debugtoolbar = None


def configure_karl(config, load_zcml=True):
    static_rev = config.registry.settings.get('static_rev')
    if not static_rev:
        static_rev = _guess_static_rev()
        config.registry.settings['static_rev'] = static_rev
    config.add_static_view('/static/%s' % static_rev, 'karl.views:static',
        cache_max_age=60 * 60 * 24 * 365)
    config.include('bottlecap')
    config.add_renderer('.pt', ux2_metarenderer_factory)
    config.registry.registerUtility(FormishZPTMetaRenderer(), IFormishRenderer)

    if load_zcml:
        config.hook_zca()
        config.include('pyramid_zcml')
        config.load_zcml('standalone.zcml')

    debug = asbool(config.registry.settings.get('debug', 'false'))
    if not debug:
        config.add_view('karl.errorpage.errorpage', context=Exception,
                        renderer="karl.views:templates/errorpage.pt")
        config.add_view('karl.errorpage.errorpage', context=NotFound,
                        renderer="karl.views:templates/errorpage.pt")
    
    
    # Debug toolbar is disabled temporarily
    ##if debug and pyramid_debugtoolbar:
    ##    config.include(pyramid_debugtoolbar)


def _guess_static_rev():
    """Guess an appropriate static revision number.

    This is only used when no deployment tool set the static_rev
    for us.  Deployment tools should set static_rev because
    karl can only guess what static revisions are appropriate,
    while deployment tools can set a system-wide revision number
    that encompasses all relevant system changes.
    """
    # If Karl is installed as an egg, we can try to get the Karl version
    # number from the egg and use that.
    _static_rev = _get_egg_rev()

    if _static_rev is not None:
        return _static_rev

    # Fallback to just using a timestamp.  This is guaranteed not to fail
    # but will create different revisions for each process, resulting in
    # some extra static resource downloads
    _static_rev = 'r%d' % int(time.time())

    return _static_rev


def _get_egg_rev():
    # Find folder that this module is contained in
    module = sys.modules[__name__]
    path = os.path.dirname(os.path.abspath(module.__file__))

    # Walk up the tree until we find the parent folder of an EGG-INFO folder.
    while path != '/':
        egg_info = os.path.join(path, 'EGG-INFO')
        if os.path.exists(egg_info):
            rev = os.path.split(path)[1]
            return 'r%d' % hash(rev)
        path = os.path.dirname(path)


ux1_to_ux2_templates = {
    'templates/layout_formish_form.pt': 'templates/formish_form.pt',
    'templates/community_tagcloud.pt': 'templates/tagcloud.pt',
    'templates/community_taglisting.pt': 'templates/taglisting.pt',
    'templates/community_showtag.pt': 'templates/showtag.pt',
    'templates/profile_showtag.pt': 'templates/showtag.pt',
}


def ux2_metarenderer_factory(info):
    """
    Use a custom renderer to choose between 'classic' and 'ux2' UI.
    """
    # Don't use metarenderer if we're specifcally already looking for
    # something in karl.ux2.  Also don't use metarender for any of the layouts.
    # We want those to be explicitly chosen from one UI or the other at the
    # point where they are used.
    if info.name.endswith('_layout.pt') or info.package is karl.ux2:
        return renderer_factory(info)

    # Does this template exist in ux2?
    name = info.name
    if ':' in name:
        name = name[name.index(':') + 1:]
    name = ux1_to_ux2_templates.get(name, name)
    if not pkg_resources.resource_exists('karl.ux2', name):
        # There's not a UX2 version, so just return the same old renderer
        # you would normally use
        return renderer_factory(info)

    # Return a renderer that chooses classic versus ux2 based on cookie
    # in request.
    classic_renderer = renderer_factory(info)
    ux2_renderer = renderer_factory(RendererHelper(
        name, karl.ux2, info.registry))
    def metarenderer(value, system):
        use_ux2 = system['request'].cookies.get('ux2_kachoo') == 'true'
        if use_ux2:
            if 'api' in value:
                del value['api']
            return ux2_renderer(value, system)
        return classic_renderer(value, system)
    return metarenderer


class FormishZPTMetaRenderer(FormishZPTRenderer):

    def __init__(self):
        self.initialized = False

    def initialize(self):
        super(FormishZPTMetaRenderer, self).__init__()
        ux1_loader = self.loader
        search_path = ux1_loader.search_path
        ux2_path = pkg_resources.resource_filename(
            'karl.ux2', 'forms/templates')
        TemplateLoader = type(ux1_loader)
        ux2_loader = TemplateLoader([ux2_path] + search_path,
                                    ux1_loader.auto_reload)

        class MetaLoader(object):
            def load(self, filename):
                request = get_current_request()
                use_ux2 = request.cookies.get('ux2_kachoo') == 'true'
                if use_ux2:
                    template = ux2_loader.load(filename)
                else:
                    template = ux1_loader.load(filename)
                return template

        self.loader = MetaLoader()
        self.initialized = True

    def __call__(self, template, args):
        if not self.initialized:
            self.initialize()
        return super(FormishZPTMetaRenderer, self).__call__(template, args)
