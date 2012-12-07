from pyramid.renderers import render_to_response
from pyramid.security import authenticated_userid
from pyramid.url import resource_url

from karl.views.api import TemplateAPI
from karl.utils import find_site
from pyramid.httpexceptions import HTTPFound

def forbidden(context, request):
    site = find_site(context)
    environ = request.environ
    referrer = environ.get('HTTP_REFERER', '')
    if authenticated_userid(request):
        # the user is authenticated but he is not allowed to access this
        # resource
        api = TemplateAPI(context, request, 'Forbidden')
        request.layout_manager.use_layout('anonymous')
        response =  render_to_response(
            'templates/forbidden.pt',
            dict(api=api,
                 login_form_url = resource_url(site, request, 'login.html'),
                 homepage_url = resource_url(site, request)),
            request=request,
            )
        response.status = '403 Forbidden'
        return response
    elif '/login.html' in referrer:
        url = request.url
        # this request came from a user submitting the login form
        login_url = resource_url(site, request, 'login.html',
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
        login_url = resource_url(site, request, 'login.html', query=query)
        return HTTPFound(location=login_url)
