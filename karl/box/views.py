import functools
import uuid

from pyramid.decorator import reify
from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPFound,
    HTTPNotFound,
)
from pyramid.request import Response
from pyramid.traversal import find_resource
from pyramid.traversal import find_root
from pyramid.view import view_config

from karl.models.interfaces import ICommunities
from karl.models.site import Site

from ..views.api import TemplateAPI
from .client import (
    BoxArchive,
    BoxClient,
)
from boxsdk.exception import BoxException


@view_config(context=Site,
             permission='create',
             name='box')
def start_box(context, request):
    assert 'box' not in context
    context['box'] = box = BoxArchive()
    return HTTPFound(request.resource_url(box))


@view_config(context=ICommunities,
             name='pseudo-community',
             request_method='GET')
def pseudo_community(context, request):
    path = request.params.get('path', None)
    if path is None:
        return HTTPNotFound
    root = find_root(context)
    url = request.resource_url(root, *path.split('/'))
    return HTTPFound(location=url)


# Work around for lack of 'view_defaults' in earlier version of Pyramid
box_view = functools.partial(
    view_config, context=BoxArchive, permission='administer')


class BoxArchiveViews(object):
    """
    Provides UI for logging in to box and receiveing credentials for use by
    the box client, as well as a simple proof of concept that allows uploading
    and downloading files from a Box account.
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @reify
    def client(self):
        return BoxClient(self.context, self.request.registry.settings)

    @box_view(
        renderer='templates/show_box.pt',
    )
    def show_box(self):
        box = self.context
        request = self.request
        page_title = 'Box'

        files = None
        if box.logged_in:
            try:
                items = self.client.client.folder(0).get_items(100)
                files = [
                    {'name': item.name,
                     'url': self.request.resource_url(
                         box, '@@download',
                         query={'id': item.id})}
                    for item in items
                ]
            except BoxException:
                # Apparently refresh tokens can expire, so this whole thing
                # may be a house of cards.  For our purposes, log user out and
                # make them log in again.
                box.logout()

        # If not logged in, set up 'state' for CSRF protection
        if not box.logged_in and not box.state:
            box.state = str(uuid.uuid4())

        return {
            'api': TemplateAPI(box, request, page_title),
            'files': files,
        }

    @box_view(
        name='box_auth'
    )
    def box_auth(self):
        box = self.context
        request = self.request

        # CSRF protection
        if request.params['state'] != box.state:
            raise HTTPBadRequest("state does not match")
        box.state = None

        # Get access token
        self.client.authorize(request.params['code'])
        return HTTPFound('/arc2box/archive_to_box.html')

    @box_view(
        name='box_logout'
    )
    def box_logout(self):
        box = self.context
        request = self.request

        # Logout
        box.logout()
        return HTTPFound('/box')

    @box_view(
        name='upload'
    )
    def box_upload(self):
        f = self.request.params['file']
        self.client.upload_file(f.file, f.filename)
        return HTTPFound(self.request.resource_url(self.context))

    @box_view(
        name='download'
    )
    def box_download(self):
        request = self.request
        content_type, stream = self.client.download_file(request.params['id'])
        block_size = 4096
        app_iter = iter(lambda: stream.read(block_size), '')
        return Response(app_iter=app_iter, content_type=content_type)

    @reify
    def redirect_uri(self):
        return self.request.resource_url(self.context, '@@box_auth')
