import os
from simplejson import JSONEncoder
from formish.widgets import Widget
from formish.widgets import Grid
from formish.widgets import Input
from formish.widgets import Checkbox
from formish.widgets import CheckedPassword

from schemaish.type import File as SchemaFile

from convertish.convert import string_converter

class RichTextWidget(Widget):
    template = 'field.KarlTinyMCE'
    type = 'Input'

class TagsWidget(Widget):
    type = 'Input'

    def __init__(self, **kw):
        self.tagdata = kw.pop('tagdata', {'records':[]})
        Widget.__init__(self, **kw)

    def _get_tagdata(self, tags=()):
        newtags = list(tags)
        newcopy = self.tagdata.copy()

        for taginfo in newcopy['records']:
            tag = taginfo['tag']
            if tag in tags:
                newtags.remove(tag)

        for tag in filter(None, newtags):
            newcopy['records'].append({'count':1, 'snippet':'', 'tag':tag})

        return newcopy

    def json_taginfo(self, tags):
        tagdata = self._get_tagdata(tags)
        return JSONEncoder().encode(tagdata)

    def to_request_data(self, field, data):
        """
        Iterate over the data, converting each one
        """
        if data is None:
            return []
        return [string_converter(field.attr.attr).from_type(d) for d in data]
    
    def from_request_data(self, field, request_data):
        """
        Iterating to convert back to the source data
        """
        
        result = filter(None,
                        [string_converter(field.attr.attr).to_type(d) for d in
                         request_data])
        return result
            
class TagsEditWidget(TagsWidget): # widget for edit forms (ajax-add-immediate)
    template = 'field.KarlTagsEdit'

class TagsAddWidget(TagsWidget): # widget for add forms (deferred til submit)
    template = 'field.KarlTagsAdd'
    
class ManageMembersWidget(Grid):
    template = 'field.KarlManageMembers'

class KarlCheckedPassword(CheckedPassword):
    template = 'field.KarlCheckedPassword'

class UserProfileLookupWidget(Input):
    template = 'field.KarlUserProfileLookup'
    
    def from_request_data(self, field, request_data):
        L = []
        for string_data in request_data:
            if self.strip is True:
                string_data = string_data.strip()
            if not string_data:
                continue
            value = string_converter(field.attr.attr).to_type(
                string_data,
                converter_options=self.converter_options)
            L.append(value)
        return L

class AcceptFieldWidget(Checkbox):
    template = 'field.KarlAcceptField'
    def __init__(self, text, description, **kw):
        self.text = text
        self.description = description
        Checkbox.__init__(self, **kw)

UNSET = object()

class FileUpload2(Widget):
    """
    Saner file upload widget; use filename as key rather than uuid.
    
    In addition: a 'single' parameter injects a hidden add field in case
    the current content is deleted. We need this parameter if the
    field is not in a sequence.

    And: support for optionally injecting add'l path into the file's
    URL path when we know we're working w/ a temporary file from the
    filestore during the current request.
    """
    type = 'FileUpload'
    template = 'field.FileUpload'
    
    def __init__(self, filestore, show_file_preview=True,
                 show_download_link=False, show_image_thumbnail=False,
                 url_base=None, css_class=None, image_thumbnail_default=None,
                 single=False, filestore_path=''):
        """
        Changes from the default implementation:
        - require ``filestore`` argument (no default)
        - we don't use any ``url_ident_factory``
        - ``single`` argument
        - ``filestore_path`` argument
        - add ``self.from_filestore`` flag which will tell the template
          when we're dealing with a temp file coming from the filestore
        """
        # Setup defaults.
        if url_base is None:
            url_base = '/filehandler'
        # Initialise instance state
        Widget.__init__(self)
        self.filestore = filestore
        self.show_image_thumbnail = show_image_thumbnail
        self.image_thumbnail_default = image_thumbnail_default
        self.url_base = url_base
        self.show_download_link = show_download_link
        self.show_file_preview = show_file_preview
        self.single = single
        self.filestore_path = filestore_path
        self.from_filestore = False

    def urlfactory(self, data):
        """
        Possibly inject filestore path into the file's URL.
        """
        if not data:
            return self.image_thumbnail_default
        url_base = self.url_base
        if not url_base.endswith('/'):
            url_base += '/'
        if self.from_filestore and self.filestore_path:
            return '%s%s/%s' % (url_base, self.filestore_path, data)
        return '%s%s' % (url_base, data)
    
    def to_request_data(self, field, data):
        """
        Varies from default in that we use the filename (w/ an
        optional path prefix) as the 'name' of our file object.
        """
        if isinstance(data, SchemaFile):
            default = data.filename
            mimetype = data.mimetype
        else:
            default = ''
            mimetype = ''
        return {'name': [default], 'default':[default], 'mimetype':[mimetype]}
    
    def pre_parse_incoming_request_data(self, field, data):
        """
        Varies from default in that we use the filename as the tmp
        file lookup key.
        """
        if data is None:
            data = {}
        if data.get('remove', [None])[0] is not None:
            data['name'] = ['']
            data['mimetype'] = ['']
            return data

        fieldstorage = data.get('file', [''])[0]
        if getattr(fieldstorage,'file',None):
            filename = fieldstorage.filename
            filename = filename.replace('\\', '/')
            key = os.path.split(filename)[-1]
            self.filestore.put(key, fieldstorage.file, key,
                               [('Content-Type', fieldstorage.type),
                                ('Filename', fieldstorage.filename)])
            data['name'] = [key]
            data['mimetype'] = [fieldstorage.type]
        return data
    
    def from_request_data(self, field, request_data):
        """
        Differs from default for better handling of SchemaFile's
        metadata when no file is in the request, and to set a flag on
        self when we're working w/ a file in the tmp filestore.
        """
        if request_data['name'] == ['']:
            remove = request_data.get('remove', [None])[0] is not None
            default = request_data.get('default', [None])[0]
            name = request_data.get('name', [None])[0]
            meta = {'remove':remove, 'default':default, 'name':name}
            return SchemaFile(None, None, None, metadata=meta)
        elif (request_data['name'] == request_data['default']
              and request_data.get('file') is None):
            # no file submitted -> no change to the file value
            return SchemaFile(None, None, None)
        else:
            key = request_data['name'][0]
            try:
                cache_tag, headers, f = self.filestore.get(key)
            except (KeyError, TypeError):
                return None
            self.from_filestore = True
            headers = dict(headers)
            return SchemaFile(f, headers['Filename'], headers['Content-Type'])

class PhotoImageWidget(FileUpload2):
    template = 'field.KarlPhotoImage'
    filestore_path = 'photo_from_filestore'

    def __init__(self, filestore, show_file_preview=True,
                 show_download_link=False, show_image_thumbnail=True,
                 url_base=None, css_class=None, image_thumbnail_default=None,
                 show_remove_checkbox=False):
        super(PhotoImageWidget, self).__init__(
            filestore, show_file_preview, show_download_link,
            show_image_thumbnail, url_base, css_class, image_thumbnail_default,
            single=True, filestore_path='photo_from_filestore')
        self.show_remove_checkbox = show_remove_checkbox

    def from_request_data(self, field, request_data):
        """
        Add some logic for figuring out whether or not to show the
        'remove' checkbox.
        """
        if request_data.get('default', [False])[0]:
            # we have a default value that can be removed
            self.show_remove_checkbox = True
        if request_data['name'] == ['']:
            remove = request_data.get('remove', [None])[0] is not None
            default = request_data.get('default', [None])[0]
            name = request_data.get('name', [None])[0]
            meta = {'remove':remove, 'default':default, 'name':name}
            return SchemaFile(None, None, None, metadata=meta)
        elif request_data['name'] == request_data['default']:
            return SchemaFile(None, None, None)
        else:
            key = request_data['name'][0]
            try:
                cache_tag, headers, f = self.filestore.get(key)
            except (KeyError, TypeError):
                return None
            # we have a photo from the filestore that can be removed
            self.show_remove_checkbox = True
            self.from_filestore = True
            headers = dict(headers)
            return SchemaFile(f, headers['Filename'], headers['Content-Type'])

class DateTime(Widget):
    template = 'field.DateTime'
