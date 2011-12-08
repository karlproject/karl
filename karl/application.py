from pyramid.events import BeforeRender

from karl.ux2.layout import LayoutManager
from karl.views.api import TemplateAPI

def add_renderer_globals(event):
    request = event['request']
    context = request.context
    settings = request.registry.settings
    bc = settings['bc']
    api = TemplateAPI(context, request)
    event['api'] = api


def configure_karl(config, load_zcml=True):
    config.include('bottlecap')
    config.add_bc_layout({'site': 'karl.ux2:templates/site_layout.pt'})
    config.add_bc_layoutmanager_factory(LayoutManager)
    config.add_subscriber(add_renderer_globals, BeforeRender)


    if load_zcml:
        config.hook_zca()
        config.include('pyramid_zcml')
        config.load_zcml('standalone.zcml')
