from repoze.bfg.configuration import Configurator

def dummy_view(context, request):
    return {}

def maintenance(global_config, **local_conf):
    config = Configurator()
    config.begin()
    config.add_static_view('static', '../views/static')
    config.add_route(name='maintenance',
                    path='/*url',
                    view=dummy_view,
                    view_renderer='down_for_maintenance.pt')
    config.end()
    return config.make_wsgi_app()
