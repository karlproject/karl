import re

from repoze.bfg.security import effective_principals
from repoze.bfg.url import model_url

from karl.content.interfaces import IImage
from karl.utils import find_tempfolder
from karl.views.batch import get_catalog_batch
from karl.views.utils import make_name

def thumb_url(image, request, size):
    """
    Return the url for displaying the image with dimensions bounded by given
    size.
    """
    assert IImage.providedBy(image), "Cannot take thumbnail of non-image."
    return model_url(image, request, 'thumb', '%dx%d.jpg' % size)

def get_images_batch(context,
                     request,
                     creator=None,   # 'My Recent' in imagedrawer
                     community=None, # 'This Community' in imagedrawer
                     batch_start=0,
                     batch_size=12,
                     sort_index='creation_date',
                     reverse=True,
                     batcher=get_catalog_batch):  # For unit testing
    search_params = dict(
        interfaces=[IImage,],
        allowed={'query': effective_principals(request), 'operator': 'or'},
        sort_index=sort_index,
        reverse=reverse,
        batch_start=batch_start,
        batch_size=batch_size,
    )

    if creator is not None:
        search_params['creator'] = creator
    if community is not None:
        search_params['path'] = community

    return batcher(context, request, **search_params)

TMP_IMG_RE = re.compile('(?P<pre><img[^>]+src=")'
                        '(?P<url>[^"]+/TEMP/(?P<tempid>[^/]+)'
                         '/thumb/(?P<width>\d+)x(?P<height>\d+)\.jpg)'
                        '(?P<post>"[^>]*>)')

def relocate_temp_images(doc, request):
    """
    Finds any <img> tags in the document body which point to images in the temp
    folder, moves those images to the attachments folder of the document and
    then rewrites the img tags to point to the new location.
    """
    attachments = doc.get_attachments()
    relocated_images = {}
    tempfolder = find_tempfolder(doc)

    def relocate(match):
        matchdict = match.groupdict()
        tempid = matchdict['tempid']
        if tempid in relocated_images:
            # Already relocated this one
            url = relocated_images[tempid]
        else:
            # Move temp image to attachments folder
            image = tempfolder[tempid]
            del tempfolder[tempid]
            name = make_name(attachments, image.filename)
            attachments[name] = image
            size = (int(matchdict['width']), int(matchdict['height']))
            url = thumb_url(image, request, size)
            relocated_images[tempid] = url
        return ''.join([matchdict['pre'], url, matchdict['post'],])

    doc.text = TMP_IMG_RE.sub(relocate, doc.text)
    tempfolder.cleanup()
