import json
import requests
from .slugify import slugify
import transaction

from persistent import Persistent
from requests_toolbelt import MultipartEncoder

from pyramid.traversal import find_root


class BoxArchive(Persistent):
    """
    Persistent object for storing client state.
    """
    access_token = None
    refresh_token = None
    state = None

    @property
    def logged_in(self):
        return bool(self.access_token)

    def logout(self):
        self.access_token = self.refresh_token = self.state = None


def find_box(context):
    """
    Find the box archive, create one if necessary.
    """
    root = find_root(context)
    box = root.get('box')
    if not box:
        root['box'] = box = BoxArchive()
    return box


class BoxClient(object):
    api_base_url = 'https://api.box.com/2.0/'
    authorize_url = 'https://app.box.com/api/oauth2/authorize'
    token_url = 'https://app.box.com/api/oauth2/token'
    upload_url = 'https://upload.box.com/api/2.0/files/content'

    def __init__(self, archive, settings):
        self.archive = archive
        self.client_id = settings.get('box.client_id')
        self.client_secret = settings.get('box.client_secret')
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=5)
        self.session.mount('https://', adapter)

    def authorize(self, code):
        """
        Turn an authorization code into an access token
        """
        response = self.session.post(self.token_url, data={
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }).json()

        box = self.archive
        box.access_token = response['access_token']
        box.refresh_token = response['refresh_token']

    def refresh(self, commit=False):
        box = self.archive
        response = self.session.post(self.token_url, data={
            'grant_type': 'refresh_token',
            'refresh_token': box.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }).json()

        if 'error' in response:
            raise BoxError(
                response['error'], response['error_description'])

        box.access_token = response['access_token']
        box.refresh_token = response['refresh_token']
        if commit:
            transaction.commit()

    def api_url(self, *path):
        return self.api_base_url + '/'.join(map(str, path))

    def api_call(self, method, url, *args, **kw):
        session_method = self.session.post
        if method == 'get':
            session_method = self.session.get
        box = self.archive
        headers = {'Authorization': 'Bearer ' + box.access_token or ''}
        if 'headers' in kw:
            headers.update(kw['headers'])
        kw['headers'] = headers
        response = session_method(url, *args, **kw)
        if response.status_code == requests.codes.unauthorized:
            # Refresh access token
            response = self.session.post(self.token_url, data={
                'grant_type': 'refresh_token',
                'refresh_token': box.refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }).json()

            if 'error' in response:
                transaction.abort()
                transaction.begin()
                box.logout()
                transaction.commit()
                raise BoxError(
                    response['error'], response['error_description'])

            box.access_token = response['access_token']
            box.refresh_token = response['refresh_token']

            kw['headers']['Authorization'] = 'Bearer ' + box.access_token
            response = session_method(url, *args, **kw)

        return response

    def download_file(self, file_id):
        response = self.api_call(
            'get',
            self.api_url('files', file_id, 'content'),
            stream=True)
        return response.headers['Content-Type'], response.raw

    def get_file_info(self, file_id):
        response = self.api_call(
            'get',
            self.api_url('files', file_id))
        return response.json()

    def root(self):
        return BoxFolder(self, 0)

    def check_token(self):
        box = self.archive
        if box.logged_in:
            # See whether or not we can actually make a call
            try:
                self.root().contents()
            except BoxError:
                # Probably refresh token has expired
                box.logout()
        return box.logged_in


class BoxFolder(object):
    _contents = None
    name = None

    def __init__(self, client, id):
        self.client = client
        self.id = id

    def _folder_listing(self):
        client = self.client
        response = client.api_call(
            'get',
            client.api_url('folders', self.id, 'items')
        )
        files = response.json()['entries']
        return files

    def contents(self):
        if self._contents is None:
            self._contents = contents = {}
            for entry in self._folder_listing():
                factory = BoxFolder if entry['type'] == 'folder' else BoxFile
                item = factory(self.client, entry['id'])
                item.name = entry['name']
                contents[item.name] = item
        return self._contents

    def items(self):
        return self.contents().items()

    def __getitem__(self, key):
        return self.contents()[key]

    def __nonzero__(self):
        return bool(self.contents())

    def __contains__(self, key):
        return key in self.contents()

    def get_or_make(self, *path):
        if not path:
            return self

        name, path = path[0], path[1:]
        if name in self:
            return self.contents()[name].get_or_make(*path)
        return self.mkdir(name).get_or_make(*path)

    def mkdir(self, name):
        client = self.client
        url = client.api_url('folders')
        data = json.dumps({
            'name': name,
            'parent': {'id': self.id}})
        response = client.api_call('post', url, data=data)
        if response.status_code == 409:
            # folder already exists, which means we are resuming failed op
            folder_id = response.json()['context_info']['conflicts'][0]['id']
        else:
            folder_id = response.json()['id']
            folder = BoxFolder(client, folder_id)
            self.contents()[name] = folder
        return folder

    def upload(self, name, f):
        # some attachment file names may have hidden new lines and tabs, ugh
        name = slugify(name)
        data = MultipartEncoder([
            ('attributes', json.dumps(
                {'name': name, 'parent': {'id': self.id}})),
            ('file', (name, f)),
        ])

        client = self.client
        response = client.api_call(
            'post',
            client.upload_url,
            data=data,
            headers={'Content-Type': data.content_type})

        if response.status_code == 409:
            # file already exists, which means we are resuming failed op
            file_id = response.json()['context_info']['conflicts']['id']
        else:
            try:
                file_id = response.json()['entries'][0]['id']
            except ValueError:
                # something went wrong, retry in case it was a network hiccup
                response = client.api_call(
                    'post',
                    client.upload_url,
                    data=data,
                    headers={'Content-Type': data.content_type})
                file_id = response.json()['entries'][0]['id']
        self.contents()[name] = uploaded = BoxFile(client, file_id)
        return uploaded


class BoxFile(object):

    def __init__(self, client, id):
        self.client = client
        self.id = id


class BoxError(Exception):

    def __init__(self, error, description):
        super(BoxError, self).__init__(description)
        self.error = error
        self.description = description
