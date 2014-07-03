from pyramid.url import resource_url

from karl.views.api import TemplateAPI
from karl.utils import find_site

def forbidden(context, request):
    site = find_site(context)
    request.session['came_from'] = request.url
    api = TemplateAPI(context, request, 'Forbidden')
    request.layout_manager.use_layout('anonymous')
    request.response.status = '403 Forbidden'
    if api.userid:
        login_url = resource_url(site, request, 'login.html')
    else:
        login_url = resource_url(
            site, request, 'login.html', query={'reason': 'Not logged in'})
    return {
        'api': api,
        'login_form_url': login_url,
        'homepage_url': resource_url(site, request)
    }
