"""
Export a community's content to the filesystem. An xml file is used to capture
the text content, and the blobs are exported to the filesystem. An "export"
directory in the current path is where it places all the files.

A sax xml generator is used to support exporting data for large communities, so
all the data isn't required to be in memory to generate the xml file.

Blobs are separated out into directories based on whether they are attached to
their context object or if they are in the files tool.

The calendar tool is not currently exported because it was not needed for this
use case. A placeholder exists if it needs to be added in the future.
"""

from datetime import datetime
from karl.content.interfaces import ICommunityFile
from karl.scripting import create_karl_argparser
from karl.utils import find_communities
from karl.utils import find_community
from karl.utils import find_tags
from xml.sax.saxutils import XMLGenerator
import logging
import os
import sys

LOGGER = "export_community"
log = logging.getLogger(LOGGER)
logging.basicConfig()

def main(argv=sys.argv):
    parser = create_karl_argparser(
        description="Export a community's data."
        )
    parser.add_argument('--community', dest='community', action='store',
                        help=('Community to export. This should be the slug. '
                              'Can separate with , to specify multiple '
                              'communities as in "c1,c2,c3".'))
    args = parser.parse_args(sys.argv[1:])

    env = args.bootstrap(args.config_uri)

    site, registry, closer = env['root'], env['registry'], env['closer']
    slugs = args.community.split(',')
    for community_slug in slugs:
        community = lookup_community(site, community_slug)
        if community is None:
            log.error('%s community not found' % community_slug)
            continue
        log.info('Found community: %s. Exporting ...' % community_slug)
        export(community)

def lookup_community(site, community_slug):
    communities = find_communities(site)
    return communities and communities.get(community_slug)

def get_community_path(community):
    parentpath = os.path.abspath('export')
    dirpath = os.path.join(parentpath, community.__name__)
    return dirpath

def ensure_dir(dirpath):
    if not os.path.isdir(dirpath):
        os.makedirs(dirpath)

def create_filesystem_structure(community):
    dirpath = get_community_path(community)
    ensure_dir(dirpath)

    filespath = os.path.join(dirpath, 'files')
    ensure_dir(filespath)

    attachmentpath = os.path.join(dirpath, 'attachments')
    ensure_dir(attachmentpath)

def create_output_file(community):
    dirpath = get_community_path(community)
    filename = 'export-%s-%s.xml' % (community.__name__,
                                     datetime.now().strftime('%Y%m%d'))
    pathname = os.path.join(dirpath, filename)
    return open(pathname, 'w')

def create_xml_generator(community, output):
    return XMLGenerator(output, 'utf-8')

def simple_element(tagname, content, xml, **attrs):
    xml.startElement(tagname, attrs)
    xml.characters(content)
    xml.endElement(tagname)

def get_tags(context):
    tags = find_tags(context)
    #community = find_community(context)
    return tags.getTags(items=[context.docid],
                        #community=[community.docid],
                        )

def export_tags(context, xml):
    xml.startElement('tags', {})

    for tag in get_tags(context):
        simple_element('tag', tag, xml)

    xml.endElement('tags')

def export_blobs(context, parentid, xml):
    blobs = [x for x in context.values()
             if ICommunityFile.providedBy(x)]
    if not blobs:
        return

    xml.startElement('attachments', {})

    community = find_community(context)
    dirpath = get_community_path(community)
    attachmentpath = os.path.join(dirpath, 'attachments')
    parentpath = os.path.join(attachmentpath, parentid)
    ensure_dir(parentpath)

    for blob in blobs:
        export_file(blob, parentpath)
        simple_element('attachment', blob.__name__, xml)

    xml.endElement('attachments')

def export_wiki(community, xml):
    xml.startElement('wiki', {})
    wiki = community['wiki']
    for wiki_page in wiki.values():
        export_wikipage(wiki_page, xml)
    xml.endElement('wiki')

def export_wikipage(wiki_page, xml):
    xml.startElement('wikipage', {})

    simple_element('slug', wiki_page.__name__, xml)
    simple_element('title', wiki_page.title, xml)
    simple_element('text', wiki_page.text, xml)
    simple_element('creator', wiki_page.creator, xml)
    simple_element('created', wiki_page.created.isoformat(), xml)
    simple_element('modified_by', wiki_page.modified_by, xml)
    simple_element('modified', wiki_page.modified.isoformat(), xml)

    export_tags(wiki_page, xml)
    export_blobs(wiki_page, wiki_page.__name__, xml)

    xml.endElement('wikipage')

def export_blog(community, xml):
    xml.startElement('blog', {})
    blog = community['blog']
    for blog_entry in blog.values():
        export_blogentry(blog_entry, xml)
    xml.endElement('blog')

def export_blogentry(blog_entry, xml):
    xml.startElement('blogentry', {})

    simple_element('slug', blog_entry.__name__, xml)
    simple_element('title', blog_entry.title, xml)
    simple_element('text', blog_entry.text, xml)
    simple_element('creator', blog_entry.creator, xml)
    simple_element('created', blog_entry.created.isoformat(), xml)
    simple_element('modified_by', blog_entry.modified_by, xml)
    simple_element('modified', blog_entry.modified.isoformat(), xml)

    export_tags(blog_entry, xml)
    export_comments(blog_entry['comments'].values(), xml)
    export_blobs(blog_entry['attachments'], blog_entry.__name__, xml)

    xml.endElement('blogentry')

def export_comments(comments, xml):
    xml.startElement('comments', {})
    for comment in comments:
        export_comment(comment, xml)
    xml.endElement('comments')

def export_comment(comment, xml):
    xml.startElement('comment', {})
    simple_element('text', comment.text, xml)
    simple_element('creator', comment.creator, xml)
    simple_element('created', comment.created.isoformat(), xml)
    xml.endElement('comment')

def export_calendar(community, xml):
    pass

CHUNK_SIZE = 1024 * 4

def export_file(fileobj, dirpath):
    filepath = os.path.join(dirpath, fileobj.__name__)
    with open(filepath, 'w') as writer:
        with fileobj.blobfile.open('r') as reader:
            while 1:
                chunk = reader.read(CHUNK_SIZE)
                if not chunk:
                    break
                writer.write(chunk)

def export_files(community, xml):
    dirpath = get_community_path(community)
    filespath = os.path.join(dirpath, 'files')

    def walk_file(fileobj, prefixpath):
        if hasattr(fileobj, 'values'):
            folderpath = os.path.join(prefixpath, fileobj.__name__)
            ensure_dir(folderpath)
            for child in fileobj.values():
                walk_file(child, folderpath)
        else:
            export_file(fileobj, prefixpath)

    for fileobj in community['files'].values():
        walk_file(fileobj, filespath)

def export_metadata(community, xml):
    simple_element('slug', community.__name__, xml)
    simple_element('title', community.title, xml)
    simple_element('overview', community.text, xml)

    xml.startElement('members', {})
    for member in community.member_names:
        simple_element('member', member, xml)
    xml.endElement('members')

    xml.startElement('moderators', {})
    for moderator in community.moderator_names:
        simple_element('moderator', moderator, xml)
    xml.endElement('moderators')

def export(community):
    create_filesystem_structure(community)
    with create_output_file(community) as output:
        xml = create_xml_generator(community, output)

        xml.startElement('community', {})

        log.info('Exporting community metadata ...')
        export_metadata(community, xml)
        log.info('Exporting community metadata done')

        log.info('Exporting wiki ...')
        export_wiki(community, xml)
        log.info('Exporting wiki done')

        log.info('Exporting blog ...')
        export_blog(community, xml)
        log.info('Exporting blog done')

        export_calendar(community, xml)

        log.info('Exporting files ...')
        export_files(community, xml)
        log.info('Exporting files done')

        xml.endElement('community')

        log.info('%s exported to %s' % (community.__name__, output.name))
