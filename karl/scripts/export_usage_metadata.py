"""
Export metadata for all content objects as a csv for usage analysis.
"""
import os
import sys
import csv
import codecs
import cStringIO
from datetime import datetime

import transaction

from optparse import OptionParser
from repoze.bfg.traversal import find_model

from karl.utils import find_site
from karl.utils import find_catalog
from karl.utils import coarse_datetime_repr

from karl.models.site import get_name
from karl.models.site import get_path
from karl.models.site import get_mimetype
from karl.models.site import get_creator

from karl.scripting import get_default_config
from karl.scripting import open_root

import logging
LOGGER = "export_usage_metadata"
log = logging.getLogger(LOGGER)
old_date = coarse_datetime_repr(datetime(1999,1,1))

def _get_docid(context):
    return context.docid
def _get_title(context):
    return getattr(context, 'title', None)
def _get_name(context):
    return get_name(context, None)
def _get_path(context):
    return get_path(context, None)
def _get_creation_date(context):
    try:
        return getattr(context, 'created').strftime("%Y-%m-%d %H:%M:%S")
    except:
        return None
def _get_modified_date(context):
    try:
        return getattr(context, 'modified').strftime("%Y-%m-%d %H:%M:%S")
    except:
        return None
def _get_mimetype(context):
    return get_mimetype(context, None)
def _get_creator(context):
    return get_creator(context, None)
def _get_public(context):
    return getattr(context, 'security_state', 'inherits') == 'public'
def _get_class_name(context):
    return context.__class__.__name__
def _get_size(context):
    return getattr(context, 'size', None)
def _get_location(context):
    return getattr(context, 'location', None)
def _get_country(context):
    return getattr(context, 'country', None)

metadata_fields = [
    ('docid', _get_docid),
    ('title', _get_title),
    ('name', _get_name),
    ('path', _get_path),
    ('created', _get_creation_date),
    ('modified', _get_modified_date),
    ('mimetype', _get_mimetype),
    ('creator', _get_creator),
    ('public', _get_public),
    ('class_name', _get_class_name),
    ('size', _get_size),
    ('location', _get_location),
    ('country', _get_country),
    #('tags', get_creator),
]

def main():
    logging.basicConfig()
    log.setLevel(logging.INFO)

    parser = OptionParser(description=__doc__,)
    parser.add_option('-C', '--config', dest='config', default=None,
        help="Specify a paster config file. Defaults to $CWD/etc/karl.ini")

    options, args = parser.parse_args()

    me = sys.argv[0]
    me = os.path.abspath(me)
    sandbox = os.path.dirname(os.path.dirname(me))
    outfile_path = os.path.join(sandbox, 'var', 'usage_metadata.csv')

    config = options.config
    if config is None:
        config = get_default_config()
    root, closer = open_root(config)

    _export_metadata(root, outfile_path)

    log.info("All done.")

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([unicode(s).encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

def _export_metadata(root, outfile_path):
    output_csv = UnicodeWriter(open(outfile_path, 'w+'))

    header = []
    for field in metadata_fields:
        header.append(field[0])
    output_csv.writerow(header)

    for metadata in _content_generator(root):
        output_csv.writerow(metadata)
    
def _content_generator(root):
    catalog = find_catalog(root)
    #results = catalog.search(creation_date={'query': old_date, 'range': 'max'})
    #address = catalog.document_map.address_for_docid

    #import pdb; pdb.set_trace()
    for path, docid in catalog.document_map.address_to_docid.items():
        metadata = []
        #path = address(docid)
        if not path:
            log.error("No path for object with docid %s", docid)
            continue
        try:
            context = find_model(root, path)
        except:
            log.error("Error when fetching object at path: %s", path)
            continue
        if not context:
            log.error("No object at path: %s", path)
            continue
        for field in metadata_fields:
            metadata.append(field[1](context))
        yield metadata
