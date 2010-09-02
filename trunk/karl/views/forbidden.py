from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.url import model_url

from karl.views.api import TemplateAPI
from karl.utils import find_site
from webob.exc import HTTPFound

def forbidden(context, request):
    site = find_site(context)
    environ = request.environ
    referrer = environ.get('HTTP_REFERER', '')
    if 'repoze.who.identity' in environ:
        # the user is authenticated but he is not allowed to access this
        # resource
        api = TemplateAPI(context, request, 'Forbidden')
        response =  render_template_to_response(
            'templates/forbidden.pt',
            api=api,
            login_form_url = model_url(site, request, 'login.html'),
            homepage_url = model_url(site, request),
            )
        response.status = '403 Forbidden'
        return response
    elif '/login.html' in referrer:
        url = request.url
        # this request came from a user submitting the login form
        login_url = model_url(site, request, 'login.html',
                              query={'reason':'Bad username or password',
                                     'came_from':url})
        return HTTPFound(location=login_url)
    else:
        # the user is not authenticated and did not come in as a result of
        # submitting the login form
        url = request.url
        query = {'came_from':url}
        while url.endswith('/'):
            url = url[:-1]
        if url != request.application_url: # if request isnt for homepage
            query['reason'] = 'Not logged in'
        login_url = model_url(site, request, 'login.html', query=query)
        return HTTPFound(location=login_url)
