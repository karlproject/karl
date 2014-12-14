import json
import requests

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


def find_box(context):
    return find_root(context).get('box', None)


class BoxClient(object):
    api_base_url = 'https://api.box.com/2.0/'
    authorize_url = 'https://app.box.com/api/oauth2/authorize'
    token_url = 'https://app.box.com/api/oauth2/token'
    upload_url = 'https://upload.box.com/api/2.0/files/content'

    def __init__(self, archive, settings):
        self.archive = archive
        self.client_id = settings.get('box.client_id')
        self.client_secret = settings.get('box.client_secret')

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

        box = self.archive
        box.access_token = response['access_token']
        box.refresh_token = response['refresh_token']

    def api_url(self, *path):
        return self.api_base_url + '/'.join(path)

    def api_call(self, method, url, *args, **kw):
        box = self.archive
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
        return files

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
