# Copyright (C) 2008-2009 Open Society Institute
#               Thomas Moroz: tmoroz@sorosny.org
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License Version 2 as published
# by the Free Software Foundation.  You may not use, modify or distribute
# this program under any other version of the GNU General Public License.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import datetime
from simplejson import JSONEncoder
import transaction
import urlparse
import os
from webob import Response

from repoze.bfg.security import authenticated_userid
from repoze.bfg.security import has_permission
from repoze.bfg.traversal import model_path
from repoze.bfg.traversal import traverse
from repoze.bfg.url import model_url
from repoze.lemonade.content import create_content
from repoze.workflow import get_workflow

from karl.content.interfaces import ICommunityFile
from karl.content.interfaces import IImage
from karl.content.views.utils import get_upload_mimetype
from karl.models.interfaces import ICommunity
from karl.utilities.image import get_images_batch
from karl.utilities.image import thumb_url
from karl.utils import find_profiles
from karl.utils import find_tempfolder
from karl.utils import find_community
from karl.views.utils import basename_of_filepath
from karl.views.utils import check_upload_size
from karl.views.utils import make_name

"""Some explanation on how the imagedrawer ajax works. The
workflow is described here.

As a principle, we want a minimum number of requests. So, each
request can aggregate various pieces of information in its
response, so that the client has everything at hand without
the need for consequent requests. The responses are json format.

None of these requests should be cacheable at all.

1. User is editing a page. She presses the 'image' button on the
   tinymce toolbar.

  - Client calls "drawer_dialog_view.html".

  - The view returns:
        {
        dialog_snippet: ...the html of the dialog
        images_info: ...the first batch of the image listing
            (in case, the initial image source needs one.
            Otherwise, it is missing. Since the server selects
            the initial image source, it knows if the images_info
            is needed and provides it. This saves one ajax
            request for the client.)
        error: ... explicitely raise an error
        }

2. User is scrolling to the next batch of images.

  - Client calls "drawer_data_view.html".

  - The view returns:
        {
        images_info: ...the selected batch of the image listing
        error: ... explicitely raise an error
        }


3. User is changing the data source or filtering (= update).

  - Client calls "drawer_data_view.html".

  - The view returns:
        {
        images_info: ...the selected batch of the image listing
        error: ... explicitely raise an error
        }


4. User is uploading a file.

  - Client posts to "drawer_upload_view.html".

  - The file content is passed in to the view as
    the "file" parameter. This file is
    saved on the server side, thumbnail generated etc.

  - The view returns:
        {
        upload_image_info: ...information aboutt the succesfully
                    uploaded file, in the same record format as used
                    in the data views.
        error: ... explicitely raise an error
        }

"""
# DISPLAY_SIZE is size of images displayed after they inserted into a document.
# This is hardcoded for now but should be chosen by user when inserting the
# image, eg: small, medium, large
DISPLAY_SIZE = (800, 800)

# Size of thumbnails displayed in image drawer when browsing images.
THUMB_SIZE = (85, 85)
LARGE_THUMB_SIZE = (175, 175)

# a somewhat useful decorator
class jsonview(object):
    def __init__(self, content_type="application/x-json"):
        self.content_type = content_type

    def __call__(self, inner):
        def wrapped(*arg, **kw):
            payload = inner(*arg, **kw)
            if 'error' in payload:
                transaction.doom()
            result = JSONEncoder().encode(payload)
            return Response(result, content_type=self.content_type)
        return wrapped

def breadcrumbs(doc, request):
    """
    Returns an iterator over each object in the path leading to 'doc'.  If
    'doc' is in a community, the path will begin with the community, otherwise
    it will begin with the site root.  For each object in the path returns
    a dict of 'title' and 'href'.
    """
    def title_or_id(context):
        return getattr(context, 'title', context.__name__)

    def visit(node):
        if not (ICommunity.providedBy(node) or
                getattr(node, '__parent__', None) is None):
            for ancestor in visit(node.__parent__):
                yield ancestor

        yield dict(title=title_or_id(node), href=model_url(node, request))

    return list(visit(doc))

def get_image_info(image, request, thumb_size=THUMB_SIZE):
    """Return the info about a particular image,
    in the format specified by the client's needs.

    This is used when:

        - a batch of images are returned

        - information about the succesfully uploaded
          image is returned

    """
    profiles = find_profiles(image)
    creator = profiles[image.creator]
    width, height = image.image_size
    image_url = urlparse.urlparse(thumb_url(image, request, DISPLAY_SIZE))

    return dict(
        name = image.__name__,
        title = image.title,
        author_name = creator.title,
        location = breadcrumbs(image, request),
        image_url = image_url.path,
        image_width = width,
        image_height = height,
        image_size = image.size,
        thumbnail_url = thumb_url(image, request, thumb_size),
        last_modified = image.modified.ctime(),  # XXX Format?
    )

# size of minimal batch, if client does not ask for it.
# only counts at the initial batch.
MINIMAL_BATCH = 12

def batch_images(context, request,
                 get_image_info=get_image_info, # unittest
                 get_images_batch=get_images_batch): # unittest

    include_image_url = request.params.get('include_image_url', None)
    # include_image_url is a special case.
    include_info = None
    if include_image_url is not None:
        # Note, we must use the path only, as IE submits the full domain
        # and without the next line IE would fail.
        path = urlparse.urlparse(include_image_url)[2]
        include_context = traverse(context, path)['context']
        if IImage.providedBy(include_context):
            # We have a good image to include.
            include_info = get_image_info(include_context, request)

    # Find query parameters based on the 'source' param,
    # which signifies the selection index of the source button
    # in the imagedrawer dialog.
    source = request.params.get('source')
    assert source in ('myrecent', 'thiscommunity', 'allkarl')

    if source == 'myrecent':
        creator = authenticated_userid(request)
        community_path = None
    elif source == 'thiscommunity':
        creator = None
        community = find_community(context)
        # batching api requires the community path
        community_path = model_path(community)
    else:               # All Karl
        creator = None
        community_path = None

    # batching
    # Decide start and size here, don't let the lower levels
    # apply their default. This allows us to enforce
    # a MINIMAL_BATCH size.
    batch_start = int(request.params.get('start', '0'))
    batch_size = int(request.params.get('limit', '0'))
    # there is a minimal batch size to enforce, if the client
    # does not ask for one
    # Just pass the values to lower levels where sensible
    # defaults will be applied.
    sort_index = request.params.get('sort_on', None)
    reverse = request.params.get('reverse', None)

    # XXX include_image will now be inserted in the first
    # position, as extra image.
    insert_extra = False
    if include_info is not None:
        if batch_start == 0:
            batch_size -= 1
            insert_extra = True
        else:
            batch_start -= 1

    # Enforce the minimal batch size
    batch_size = max(batch_size, MINIMAL_BATCH)

    search_params = dict(
        creator=creator,
        community=community_path,
        batch_start=batch_start,
        batch_size=batch_size,
    )
    if sort_index:
        search_params['sort_index'] = sort_index
    if reverse:
        search_params['reverse'] = bool(int(reverse))

    batch_info = get_images_batch(
        context,
        request,
        **search_params
    )

    records = [get_image_info(image, request)
               for image in batch_info['entries']]
    start = batch_info['batch_start']
    totalRecords = batch_info['total']

    # add the fake included image
    if include_info is not None:
        totalRecords += 1
        if insert_extra:
            records.insert(0, include_info)
        else:
            start += 1

    return dict(
        records = records,
        start = start,
        totalRecords = totalRecords,
        )

@jsonview()
def drawer_dialog_view(context, request,
                       batch_images=batch_images): # unittest
    """This view returns a json reply that is a dictionary containing:

        dialog_snippet: the html of the dialog

        [[images_info: the first batch of the image listing
          * since the default source is now upload which is
          a non-data source, this value is omitted.
          ]]

        error: ... explicitely raise an error
    """
    # Read the dialog snippet
    # It is located where the tinymce plugin is.
    here = os.path.abspath(os.path.dirname(__file__))
    dialog_snippet = file(os.path.join(here,
            'static', 'tinymce', '3.3.9.2', 'plugins', 'imagedrawer',
            'imagedrawer_dialog_snippet.html',
        )).read()

    d = dict(
        dialog_snippet = dialog_snippet,
        )

    # Download sources will need a batch result
    # to be included in the response.
    source = request.params.get('source', None)
    assert source in ('upload', 'myrecent', 'thiscommunity',
                    'allkarl', 'external', None)
    if source in ('myrecent', 'thiscommunity', 'allkarl'):
        d['images_info'] = batch_images(context, request)

    return d

@jsonview()
def drawer_data_view(context, request,
                     batch_images=batch_images):  # unittest
    """This view returns a json reply that is a dictionary containing:

        images_info: the selected batch of the image listing

        error: ... explicitely raise an error
    """
    return dict(
        images_info=batch_images(context, request),
    )


# We must lie about the content type in order to
# let the browser load it into the iframe without complaining
@jsonview(content_type="text/html")
def drawer_upload_view(context, request,
                       check_upload_size=check_upload_size,
                       get_image_info=get_image_info,
                       batch_images=batch_images,
                       ):
    """Drawer posts a file with the parameter name "file".
    """

    ## XXX The rest is copied from add_file_view. A common denominator
    ## would be desirable.

    creator = authenticated_userid(request)

    fieldstorage = request.params.get('file')
    if not hasattr(fieldstorage, 'filename'):
        msg = 'You must select a file before clicking Upload.'
        return dict(error = msg)

    # For file objects, OSI's policy is to store the upload file's
    # filename as the objectid, instead of basing __name__ on the
    # title field).
    filename = basename_of_filepath(fieldstorage.filename)

    stream = fieldstorage.file
    # use parameter, as the title (or basename, if missing).
    title = request.params.get('title', filename)
    image = create_content(ICommunityFile,
                          title=title,
                          stream=stream,
                          mimetype=get_upload_mimetype(fieldstorage),
                          filename=fieldstorage.filename,
                          creator=creator,
                          )
    # Check if it's an image.
    if not IImage.providedBy(image):
        msg = 'File %s is not an image' % filename
        return dict(error=msg)

    check_upload_size(context, image, 'file')

    if hasattr(context, 'get_attachments'):
        target_folder = context.get_attachments()
        if not has_permission('create', target_folder, request):
            msg = 'You do not have permission to upload files here.'
            return dict(error=msg)

        image.filename = filename
        name = make_name(target_folder, filename, raise_error=False)
        if not name:
            msg = 'The filename must not be empty'
            return dict(error=msg)

        # Is there a key in context with that filename?
        if name in target_folder:
            msg = 'Filename %s already exists in this folder' % filename
            return dict(error=msg)

        target_folder[name] = image

        workflow = get_workflow(ICommunityFile, 'security', context)
        if workflow is not None:
            workflow.initialize(image)

    # In cases where the image is to live in a piece of content which has not
    # yet been created (like when using an 'Add' form), the context is going
    # to be the eventual parent of the not yet created content, which will be
    # the eventual parent of the just now created image.  Since we have nowhere
    # to put the image, we put it in a tempfolder and later move it over after
    # the content is created.  Normal ContentAdded event handlers are not
    # called at this stage and workflow is not yet initialized.  These will
    # occur when the content is moved over.
    else:
        image.modified = datetime.datetime.now()
        tempfolder = find_tempfolder(context)
        tempfolder.add_document(image)


    # Return info about the image uploaded
    return dict(
        upload_image_info=get_image_info(image, request, thumb_size=LARGE_THUMB_SIZE),
    )
