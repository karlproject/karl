import sys
import transaction

from pyramid.traversal import model_path
from karl.content.models.blog import MailinTraceBlog
from karl.scripting import create_karl_argparser
from karl.utils import find_communities


def main(argv=sys.argv):
    parser =  create_karl_argparser(
        description='Add a fake blog tool to community for receiving mailin '
        'trace emails.'
        )
    parser.add_argument('community', help='Community name.')
    parser.add_argument('file', help='Path to file to touch when a tracer '
                                     'email is received.')
    args = parser.parse_args(argv[1:])
    env = args.bootstrap(args.config_uri)
    root, closer = env['root'], env['closer']
    root, closer = args.get_root(args.inst)
    community = find_communities(root).get(args.community)
    if community is None:
        args.parser.error('Could not find community: %s' % args.community)

    blog = community.get('blog')
    if blog is not None:
        if len(blog) > 0:
            args.parser.error('Cannot replace blog with blog entries.')
        else:
            del community['blog']

    community['blog'] = blog = MailinTraceBlog()
    out = args.out
    print >> out, 'Added mailin trace tool at: %s' % model_path(blog)

    settings = root._p_jar.root.instance_config
    settings['mailin_trace_file'] = args.file
    print >> out, 'The mailin trace file is: %s' % args.file

    transaction.commit()
    print >> out, ('You must restart the mailin daemon in order for the new '
                   'settings to take effect.')
