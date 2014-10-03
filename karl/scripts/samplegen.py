import sys
import transaction

from karl.utilities.samplegen import add_sample_community
from karl.utilities.samplegen import add_sample_users
from karl.scripting import create_karl_argparser

def main(argv=sys.argv):
    parser = create_karl_argparser(
        description='Generate sample content in the database.'
        )
    parser.add_argument('-c', '--communities', dest='communities',
        help='Number of communities to add (default 10)', default=10)
    parser.add_argument('--dry-run', dest='dryrun',
        action='store_true',
        help="Don't actually commit the transaction")
    parser.add_argument('-m', '--more-files', dest='more_files',
        action='store_true',
        help="Create many files in the first community (default false)")
    args = parser.parse_args(argv[1:])
    env = args.bootstrap(args.config_uri)
    root, closer = env['root'], env['closer']
    try:
        add_sample_users(root)
        for i in range(int(args.communities)):
            try:
                add_sample_community(
                    root,
                    more_files=(args.more_files and i==0)
                    )
            except TypeError:
                # fall back for old versions that do not support more_files
                add_sample_community(root)
    except:
        transaction.abort()
        raise
    else:
        if args.dryrun:
            transaction.abort()
        else:
            transaction.commit()
