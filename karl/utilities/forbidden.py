from zope.interface import classProvides
from paste.request import construct_url

from webob import Request
from repoze.bfg.chameleon_zpt import render_template
from repoze.bfg.url import model_url
from repoze.bfg.interfaces import IUnauthorizedAppFactory

from karl.views.api import TemplateAPI
from karl.utils import find_site

class Forbidden:
    classProvides(IUnauthorizedAppFactory)
    def __call__(self, environ, start_response):
        request = Request(environ=environ)
        context = request.context
        site = find_site(context)
        referrer = environ.get('HTTP_REFERER', '')
        if 'repoze.who.identity' in environ:
            # the user is authenticated but he is not allowed to access this
            # resource
            api = TemplateAPI(context, request, 'Forbidden')
            body =  render_template(
                'templates/forbidden.pt',
                api=api,
                login_form_url = model_url(site, request, 'login.html'),
                homepage_url = model_url(site, request),
                )
            headerlist = []
            headerlist.append(('Content-Type', 'text/html; charset=utf-8'))
            headerlist.append(('Content-Length', str(len(body))))
            start_response('403 Forbidden', headerlist)
            if isinstance(body, unicode):
                body = body.encode('utf-8')
            return [body]
        elif '/login.html' in referrer:
            # this request came from a user submitting the login form
            login_url = model_url(site, request, 'login.html',
                                  query={'reason':'Bad username or password',
                                         'came_from':construct_url(environ)})
            start_response('302 Found', [('Location', login_url)])
            return ''
        else:
            # the user is not authenticated and did not come in as a result of
            # submitting the login form
            query = {'came_from':construct_url(environ)}
            url = request.url
            while url.endswith('/'):
                url = url[:-1]
            if url != request.application_url: # if request isnt for homepage
                query['reason'] = 'Not logged in'
            login_url = model_url(site, request, 'login.html', query=query)
            start_response('302 Found', [('Location', login_url)])
            return ''


