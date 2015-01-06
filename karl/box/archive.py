import logging
import os
import shutil

from cStringIO import StringIO
from pyramid.renderers import render
from pyramid.traversal import find_resource, lineage, resource_path

from karl.content.interfaces import ICommunityFolder
from karl.security.workflow import postorder
from karl.utils import find_catalog, find_profiles, find_tags

from .client import find_box, BoxClient
from .queue import RedisArchiveQueue


log = logging.getLogger(__name__)


def archive(community):
    """
    Returns an `ArchiveFolder` representing an archived community, whose
    contents are representations of the files and subfolders that make up an
    archived community.
    """
    folder = ArchiveFolder()
    folder['index.html'] = ArchiveTemplate(
        'templates/archive_community.pt',
        community=community)
    if 'blog' in community:
        folder['blog'] = archive_blog(community)
    if 'files' in community:
        folder['files'] = archive_files(community, community['files'], path=())
    return folder


def archive_blog(community):
    """
    Archive a blog.
    """
    blog = community['blog']
    folder = ArchiveFolder()
    folder['__attachments__'] = attachments = ArchiveFolder()
    entries = []
    for name, entry in blog.items():
        url = name + '.html'
        author = get_author(entry)
        for attachment in entry['attachments'].values():
            attachments[attachment.filename] = attachment.blobfile
        comments = []
        for comment in entry['comments'].values():
            for attachment in comment.values():
                attachments[attachment.filename] = attachment.blobfile
            comments.append({
                'title': comment.title,
                'author': get_author(comment),
                'date': str(comment.created),
                'text': comment.text,
                'attachments': [
                    {'title': attachment.title,
                     'url': '__attachments__/' + attachment.filename}
                    for attachment in comment.values()]
            })
        entries.append({
            'url': url,
            'title': entry.title,
            'author': author,
            'date': str(entry.created),
            'description': entry.description,
        })
        folder[url] = ArchiveTemplate(
            'templates/archive_blogentry.pt',
            community=community,
            entry=entry,
            author=author,
            attachments=[
                {'title': attachment.title,
                 'url': '__attachments__/' + attachment.filename}
                for attachment in entry['attachments'].values()],
            comments=comments,
        )
    folder['index.html'] = ArchiveTemplate(
        'templates/archive_blog.pt',
        community=community,
        entries=entries)
    return folder


def archive_files(community, files, path):
    folder = ArchiveFolder()
    contents = []
    for name, file in files.items():
        if ICommunityFolder.providedBy(file):
            folder[name] = archive_files(community, file, path + (name,))
            contents.append({
                'type': 'folder',
                'title': file.title + ' /',
                'url': file.__name__ + '/index.html',
            })
        else:
            folder[name] = file.blobfile
            contents.append({
                'type': 'file',
                'title': file.title,
                'url': file.__name__,
                'author': get_author(file),
                'date': str(file.created)
            })

    folder['index.html'] = ArchiveTemplate(
        'templates/archive_files.pt',
        community=community,
        title=files.title,
        path=path,
        contents=contents,
    )
    return folder


def get_author(context):
    profiles = find_profiles(context)
    author = profiles.get(context.creator)
    return author.title if author else 'Unknown User'


class ArchiveFolder(dict):
    """
    A folder representation of archived community content.
    """


class ArchiveFile(object):
    """
    Represents a file in an archived community.
    """
    def open(self):
        raise NotImplementedError


class ArchiveTemplate(ArchiveFile):
    """
    Lazily renders template.
    """
    def __init__(self, renderer, **context):
        self.renderer = renderer
        self.context = context

    def open(self):
        text = render(self.renderer, self.context)
        assert isinstance(text, unicode)
        return StringIO(text.encode('utf8'))


def realize_archive_to_fs(archive, path):
    """
    Write an archive representation to the filesystem.
    """
    os.mkdir(path)
    for name, item in archive.items():
        subpath = os.path.join(path, name)
        if isinstance(item, ArchiveFolder):
            realize_archive_to_fs(item, subpath)
        else:
            shutil.copyfileobj(item.open(), open(subpath, 'wb'))


def copy_community_to_box(community):
    box = BoxClient(find_box(community), get_current_registry().settings)

    def realize_archive(archive, folder):
        for name, item in archive.items():
            if isinstance(item, ArchiveFolder):
                if name in folder:
                    subfolder = folder[name]
                else:
                    subfolder = folder.mkdir(name)
                realize_archive(item, subfolder)
            else:
                folder.upload(name, item.open())

    path = reversed([o.__name__ for o in lineage(community) if o.__name__])
    folder = box.root().get_or_make('Karl Archive', *path)
    if folder:
        raise ValueError(
            'Cannot archive community, folder already exists: %s' % (
                '/' + '/'.join(path)))

    realize_archive(archive(community), folder)
    community.archive_status = 'reviewing'


def mothball_community(community):
    catalog = find_catalog(community)
    tags = find_tags(community)
    def get_docid(doc):
        return catalog.document_map.docid_for_address(resource_path(doc))

    # Unindex all documents, remove top level tools
    # Make copy of items so we're not mutating a BTree while traversing it
    for name, tool in list(community.items()):
        if name == 'members':
            # We probably want to hang on to historical membership data
            continue
        for doc in postorder(tool):  # includes tool in traversal
            docid = get_docid(doc)
            tags.delete(docid)
            catalog.unindex_doc(docid)
        del community[name]

    docid = get_docid(community)
    tags.delete(docid)
    catalog.unindex_doc(docid)

    text = 'This community has been archived.'
    community.description = community.text = text
    community.archive_status = 'archived'


import transaction
from optparse import OptionParser
from pyramid.threadlocal import get_current_registry
from karl.scripting import get_default_config
from karl.scripting import open_root


def archive_console():
    """
    A console script which archives a community to the local filesystem.  Used
    for testing.
    """
    usage = "usage: %prog [options] community destination"
    parser = OptionParser(usage, description=__doc__)
    parser.add_option('-C', '--config', dest='config', default=None,
        help="Specify a paster config file. Defaults to $CWD/etc/karl.ini")

    options, args = parser.parse_args()
    if len(args) < 2:
        parser.error("Not enough arguments.")
    community_name = args.pop(0)
    path = args.pop(0)

    if args:
        parser.error("Too many parameters: %s" % repr(args))

    if os.path.exists(path):
        parser.error("Folder already exists: %s" % path)

    config = options.config
    if config is None:
        config = get_default_config()
    root, closer = open_root(config)

    community = root['communities'].get(community_name)
    if not community:
        parser.error("No such community: %s" % community_name)

    realize_archive_to_fs(archive(community), os.path.abspath(path))


def worker():
    """
    Console script which connects to Redis and pops one unit of work off of
    either the copy queue or the remove queue and performs the required
    operation.  If no work is queued for it to do, it will block, waiting for
    work.  This command does not loop.  Once one community is copied or
    removed, the command exits.  The intent is that for looping behavior, this
    can be run from supervisor which will automatically restart the command
    after it exits.  This insures that all connection caches, etc, are cleaned
    up on each iteration.
    """
    usage = "usage: %prog [options]"
    parser = OptionParser(usage, description=__doc__)
    parser.add_option('-C', '--config', dest='config', default=None,
        help="Specify a paster config file. Defaults to $CWD/etc/karl.ini")

    options, args = parser.parse_args()
    if args:
        parser.error("Too many arguments.")

    config = options.config
    if config is None:
        config = get_default_config()
    root, closer = open_root(config)

    registry = get_current_registry()
    queue = RedisArchiveQueue.from_settings(registry.settings)
    operation, community = next(work_queue(queue, root))
    if operation == queue.COPY_QUEUE_KEY:
        copy_community_to_box(community)
    elif operation == queue.MOTHBALL_QUEUE_KEY:
        mothball_community(community)
    else:
        log.warn("unknown operation: %s", operation)

    transaction.commit()


def work_queue(queue, root):
    """
    A generator which represents the work queue, yields tuples of
    (operation, community)
    """
    while True:
        operation, path = queue.get_work()
        community = find_resource(root, path)

        # If a copy operation has been stopped since the community was enqueued
        # for copying, the community will have lost its archive_status and
        # should be skipped.
        if hasattr(community, 'archive_status'):
            yield operation, community
