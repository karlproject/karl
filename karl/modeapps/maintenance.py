from pyramid.config import Configurator

def dummy_view(context, request):
    return {
        'static': request.application_url + "/static"
    }

def maintenance(global_config, **local_conf):
    config = Configurator()
    config.add_static_view('static', 'karl.views:static')
    config.add_route(name='maintenance', path='/*url')
    config.add_view(dummy_view, renderer='down_for_maintenance.pt',
                    route_name='maintenance')
    return config.make_wsgi_app()
