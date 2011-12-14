import pkg_resources

from pyramid.chameleon_zpt import renderer_factory
from pyramid.renderers import RendererHelper
from pyramid.events import BeforeRender

import karl.ux2
from karl.ux2.layout import LayoutManager
from karl.views.api import TemplateAPI


def add_renderer_globals(event):
    request = event['request']
    context = request.context
    api = TemplateAPI(context, request)
    event['api'] = api


def configure_karl(config, load_zcml=True):
    config.include('bottlecap')
    config.add_bc_layout({'site': 'karl.ux2:templates/site_layout.pt'})
    config.add_bc_layoutmanager_factory(LayoutManager)
    config.add_subscriber(add_renderer_globals, BeforeRender)
    config.add_renderer('.pt', ux2_metarenderer_factory)

    if load_zcml:
        config.hook_zca()
        config.include('pyramid_zcml')
        config.load_zcml('standalone.zcml')


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
            return ux2_renderer(value, system)
        return classic_renderer(value, system)
    return metarenderer
