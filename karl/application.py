import pkg_resources

from pyramid.chameleon_zpt import renderer_factory
from pyramid.renderers import RendererHelper
from pyramid.threadlocal import get_current_request

from pyramid_formish import IFormishRenderer
from pyramid_formish import ZPTRenderer as FormishZPTRenderer

import karl.ux2
from karl.utils import asbool


try:
    import pyramid_debugtoolbar
    pyramid_debugtoolbar  # pyflakes stfu
except ImportError:
    pyramid_debugtoolbar = None


def configure_karl(config, load_zcml=True):
    config.include('bottlecap')
    config.add_renderer('.pt', ux2_metarenderer_factory)
    config.registry.registerUtility(FormishZPTMetaRenderer(), IFormishRenderer)

    if load_zcml:
        config.hook_zca()
        config.include('pyramid_zcml')
        config.load_zcml('standalone.zcml')

    debug = asbool(config.registry.settings.get('debug', 'false'))
    if debug and pyramid_debugtoolbar:
        config.include(pyramid_debugtoolbar)


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
        use_ux2 = system['request'].cookies.get('ux2') == 'true'
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
                use_ux2 = request.cookies.get('ux2') == 'true'
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
