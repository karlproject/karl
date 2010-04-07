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

from simplejson import JSONEncoder
import transaction
from webob import Response

from repoze.bfg.chameleon_zpt import render_template
from repoze.bfg.security import authenticated_userid
from repoze.bfg.security import has_permission
from repoze.bfg.traversal import model_path
from repoze.bfg.url import model_url
from repoze.lemonade.content import create_content
from repoze.workflow import get_workflow

from karl.content.interfaces import ICommunityFile
from karl.content.views.files import get_upload_mimetype
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
        fileinfo: ...information (name, size) of the succesfully
                     uploaded file. XXX This should be replaced
                     by the same record as what images_info returns.
        images_info: ...an update of the current image listing
                     (since the client needs to update the thumbnails)
        error: ... explicitely raise an error
        }

"""
# DISPLAY_SIZE is size of images displayed after they inserted into a document.
# This is hardcoded for now but should be chosen by user when inserting the
# image, eg: small, medium, large
DISPLAY_SIZE = (400, 400)

# Size of thumbnails displayed in image drawer when browsing images.
THUMB_SIZE = (85, 85)

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
    def visit(node):
        if not (ICommunity.providedBy(node) or
                getattr(node, '__parent__', None) is None):
            for ancestor in visit(node.__parent__):
                yield ancestor

        yield dict(title=node.title, href=model_url(node, request))

    return list(visit(doc))

def get_image_info(image, request):
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

    return dict(
        name = image.__name__,
        title = image.title,
        author_name = creator.title,
        location = breadcrumbs(image, request),
        image_url = thumb_url(image, request, DISPLAY_SIZE),
        image_width = width,
        image_height = height,
        image_size = image.size,
        thumbnail_url = thumb_url(image, request, THUMB_SIZE),
        last_modified = image.modified.ctime(),  # XXX Format?
    )

# size of minimal batch, if client does not ask for it.
# only counts at the initial batch.
MINIMAL_BATCH = 12

def batch_images(context, request,
                 get_image_info=get_image_info, # unittest
                 get_images_batch=get_images_batch): # unittest

    # Find query parameters based on the 'source' param,
    # which signifies the selection index of the source button
    # in the imagedrawer dialog.
    source = int(request.params.get('source', '0'))
    if source == 0:     # My Recent
        creator = 'admin'
        community_path = None
    elif source == 1:   # This Community
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
    batch_size = max(int(request.params.get('limit', '0')), MINIMAL_BATCH)
    # there is a minimal batch size to enforce, if the client
    # does not ask for one
    # Just pass the values to lower levels where sensible
    # defaults will be applied.
    sort_index = request.params.get('sort_on', None)
    reverse = request.params.get('reverse', None)

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

    return dict(
        records=records,
        start=batch_info['batch_start'],
        totalRecords=batch_info['total'],
    )

@jsonview()
def drawer_dialog_view(context, request,
                       batch_images=batch_images): # unittest
    """This view returns a json reply that is a dictionary containing:

        dialog_snippet: the html of the dialog

        images_info: the first batch of the image listing

        error: ... explicitely raise an error
    """
    # Render the dialog template
    dialog_snippet = render_template('templates/imagedrawer_dialog_snippet.pt',
        )

    return dict(
        dialog_snippet=dialog_snippet,
        images_info=batch_images(context, request),
    )

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

    stream = fieldstorage.file
    title = fieldstorage.filename
    image = create_content(ICommunityFile,
                          title=title,
                          stream=stream,
                          mimetype=get_upload_mimetype(fieldstorage),
                          filename=fieldstorage.filename,
                          creator=creator,
                          )
    check_upload_size(context, image, 'file')

    if hasattr(context, 'get_attachments'):
        target_folder = context.get_attachments()
        if not has_permission('create', target_folder, request):
            msg = 'You do not have permission to upload files here.'
            return dict(error=msg)

        # For file objects, OSI's policy is to store the upload file's
        # filename as the objectid, instead of basing __name__ on the
        # title field).
        filename = basename_of_filepath(fieldstorage.filename)
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

    else:
        tempfolder = find_tempfolder(context)
        tempfolder.add_document(image)

    workflow = get_workflow(ICommunityFile, 'security', context)
    if workflow is not None:
        workflow.initialize(image)

    # Update the thumbnails
    return dict(
        upload_image_info=get_image_info(image, request),
        images_info=batch_images(context, request),
    )
