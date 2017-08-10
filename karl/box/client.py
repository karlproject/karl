import boxsdk
import persistent
import pyramid.traversal
import transaction

class BoxArchive(persistent.Persistent):
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

    def store(self, access_token, refresh_token):
        self.access_token = access_token
        self.refresh_token = refresh_token
        transaction.commit()

def find_box(context):
    """
    Find the box archive, create one if necessary.
    """
    root = pyramid.traversal.find_root(context)
    box = root.get('box')
    if not box:
        root['box'] = box = BoxArchive()
    return box

class BoxClient(object):
    authorize_url = 'https://app.box.com/api/oauth2/authorize'

    def __init__(self, archive, settings):
        self.archive = archive
        self.client_id = settings.get('box.client_id')
        self.client_secret = settings.get('box.client_secret')
        self.oauth = boxsdk.OAuth2(
            client_id=self.client_id,
            client_secret=self.client_secret,
            access_token = archive.access_token,
            refresh_token = archive.refresh_token,
            store_tokens = archive.store
            )
        self.client = boxsdk.Client(self.oauth)

    def refresh(self):
        self.archive.store(*self.oauth.refresh(self.archive.access_token))

    def authorize(self, code):
        """
        Turn an authorization code into an access token
        """
        self.archive.store(*self.oauth.authenticate(code))

    def _get_or_make(self, folder, path):
        if path:
            contents = self.contents(folder)
            name = path[0]
            path = path[1:]
            if name in contents:
                folder = contents[name]
            else:
                folder = folder.create_subfolder(name)

            return self._get_or_make(folder, path)
        else:
            return folder

    def get_or_make(self, *path):
        return self._get_or_make(self.client.folder(folder_id='0'), path)

    def contents(self, folder):
        data = {}
        offset = 0
        while 1:
            items = folder.get_items(9999, offset)
            if items:
                for item in items:
                    data[item.name] = item
                offset += len(items)
            else:
                return data
