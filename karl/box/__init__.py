import functools
import json
import requests
import uuid

from persistent import Persistent
from requests_toolbelt import MultipartEncoder

from pyramid.decorator import reify
from pyramid.exceptions import NotFound
from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPFound,
)
from pyramid.response import Response
from pyramid.traversal import find_root
from pyramid.view import view_config

from karl.models.site import Site
from karl.views.api import TemplateAPI


class BoxArchive(Persistent):
    """
    Place to stash some state.
    """
    access_token = None
    refresh_token = None
    state = None

    @property
    def logged_in(self):
        return bool(self.access_token)


def find_box(context):
    return find_root(context).get('box', None)


@view_config(context=Site,
             permission='create',
             name='start_box')
def start_box(context, request):
    if find_box(context):
        raise NotFound
    context['box'] = box = BoxArchive()
    return HTTPFound(request.resource_url(box))


# Work around for lack of 'view_defaults' in earlier version of Pyramid
box_view = functools.partial(
    view_config, context=BoxArchive, permission='administer')


class BoxArchiveViews(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @box_view(
        renderer='templates/show_box.pt',
    )
    def show_box(self):
        box = self.context
        request = self.request
        page_title = 'Box'

        # If not logged in, set up 'state' for CSRF protection
        if not box.logged_in and not box.state:
            box.state = str(uuid.uuid4())
            files = None
        else:
            files = self.folder_listing()

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
        self.authorize(request.params['code'])
        return HTTPFound(request.resource_url(box))

    @box_view(
        name='upload'
    )
    def box_upload(self):
        f = self.request.params['file']
        self.upload_file(f.file, f.filename)
        return HTTPFound(self.request.resource_url(self.context))

    @box_view(
        name='download'
    )
    def box_download(self):
        request = self.request
        content_type, stream = self.download_file(request.params['id'])
        block_size = 4096
        app_iter = iter(lambda: stream.read(block_size), '')
        return Response(app_iter=app_iter, content_type=content_type)

    @reify
    def client_id(self):
        return self.request.registry.settings.get('box.client_id')

    @reify
    def client_secret(self):
        return self.request.registry.settings.get('box.client_secret')

    @reify
    def redirect_uri(self):
        return self.request.resource_url(self.context, '@@box_auth')

    authorize_url = 'https://app.box.com/api/oauth2/authorize'
    token_url = 'https://app.box.com/api/oauth2/token'

    def authorize(self, code):
        """
        Turn an authorization code into an access token
        """
        response = requests.post(self.token_url, data={
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }).json()

        box = self.context
        box.access_token = response['access_token']
        box.refresh_token = response['refresh_token']

    api_base_url = 'https://api.box.com/2.0/'

    def api_url(self, *path):
        return self.api_base_url + '/'.join(path)

    def api_call(self, method, url, *args, **kw):
        box = self.context
        headers = {'Authorization': 'Bearer ' + box.access_token}
        if 'headers' in kw:
            headers.update(kw['headers'])
        kw['headers'] = headers
        response = method(url, *args, **kw)
        if response.status_code == requests.codes.unauthorized:
            # Refresh access token
            response = requests.post(self.token_url, data={
                'grant_type': 'refresh_token',
                'refresh_token': box.refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }).json()

            box.access_token = response['access_token']
            box.refresh_token = response['refresh_token']

            kw['headers']['Authorization'] = 'Bearer ' + box.access_token
            response = method(url, *args, **kw)

        return response

    def folder_listing(self, folder_id='0'):
        response = self.api_call(
            requests.get,
            self.api_url('folders', folder_id, 'items')
        )
        files = response.json()['entries']
        for f in files:
            f['url'] = self.request.resource_url(
                self.context, '@@download',
                query={'id': f['id']})
        return files

    upload_url = 'https://upload.box.com/api/2.0/files/content'

    def upload_file(self, f, name, folder_id='0'):
        data = MultipartEncoder([
            ('attributes', json.dumps(
                {'name': name, 'parent': {'id': folder_id}})),
            ('file', (name, f)),
        ])
        # Get a refresh out of the way before trying to upload something,
        # and make sure folder actually exists
        self.folder_listing(folder_id)

        return self.api_call(
            requests.post,
            self.upload_url,
            data=data,
            headers={'Content-Type': data.content_type})

    def download_file(self, file_id):
        response = self.api_call(
            requests.get,
            self.api_url('files', file_id, 'content'),
            stream=True)
        return response.headers['Content-Type'], response.raw

    def get_file_info(self, file_id):
        response = self.api_call(
            requests.get,
            self.api_url('files', file_id))
        return response.json()


def includeme(config):
    config.scan()
