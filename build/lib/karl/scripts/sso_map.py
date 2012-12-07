from persistent.mapping import PersistentMapping
from karl.utils import find_users
import sys
import transaction


def config_parser(name, subparsers, **helpers):
    parser = subparsers.add_parser(
        name, help='Operations for mapping SSO credentials to Karl users')
    subparsers = parser.add_subparsers(title='command', help='Feed commands.')
    config_show(subparsers, **helpers)
    config_showall(subparsers, **helpers)
    config_mapuser(subparsers, **helpers)
    config_mapusers(subparsers, **helpers)
    config_remove(subparsers, **helpers)


def config_show(subparsers, **helpers):
    parser = subparsers.add_parser('show', help='Show a mapping.')
    parser.add_argument('inst', metavar='instance', help='Karl instance.')
    parser.add_argument('user', help='A Karl userid or an SSO principal.')
    parser.set_defaults(func=show, parser=parser)


def config_showall(subparsers, **helpers):
    parser = subparsers.add_parser('showall', help='List all mappings.')
    parser.add_argument('inst', metavar='instance', help='Karl instance.')
    parser.set_defaults(func=showall, parser=parser)


def config_mapuser(subparsers, **helpers):
    parser = subparsers.add_parser('mapuser', help='Map a single user.')
    parser.add_argument('inst', metavar='instance', help='Karl instance.')
    parser.add_argument('userid',
                        help='Karl userid. May be different from login.')
    parser.add_argument('principal',
        help='SSO principal, including realm and domain if Kerberos')
    parser.set_defaults(func=mapuser, parser=parser)


def config_mapusers(subparsers, **helpers):
    parser = subparsers.add_parser('mapusers',
        help='Map many users.  User mappings are read from standard input, one '
             'per line.  Each line consists of a Karl userid followed '
             'by an SSO principal, separated by white space.')
    parser.add_argument('inst', metavar='instance', help='Karl instance.')
    parser.set_defaults(func=mapusers, parser=parser)


def config_remove(subparsers, **helpers):
    parser = subparsers.add_parser('remove', help='Remove a mapping')
    parser.add_argument('inst', metavar='instance', help='Karl instance.')
    parser.add_argument('user', help='A Karl userid or an SSO principal.')
    parser.set_defaults(func=remove, parser=parser)


def mapuser(args):
    root, closer = args.get_root(args.inst)
    users = find_users(root)
    if not hasattr(users, 'sso_map'):
        users.sso_map = PersistentMapping()
    if not users.get(args.userid):
        args.parser.error("No such userid: %s" % args.userid)
    users.sso_map[args.principal] = args.userid
    transaction.commit()


def mapusers(args):
    root, closer = args.get_root(args.inst)
    users = find_users(root)
    if not hasattr(users, 'sso_map'):
        users.sso_map = PersistentMapping()
    for line in sys.stdin:
        userid, principal = line.split()
        if not users.get(userid):
            args.parser.error("No such userid: %s" % userid)
        users.sso_map[principal] = userid
    transaction.commit()


def show(args):
    root, closer = args.get_root(args.inst)
    users = find_users(root)
    mapping = getattr(users, 'sso_map', None)
    if not mapping:
        return
    userid = mapping.get(args.user)
    if userid:
        print userid
        return
    for principal, userid in mapping.items():
        if userid == args.user:
            print principal
            break


def showall(args):
    root, closer = args.get_root(args.inst)
    users = find_users(root)
    mapping = getattr(users, 'sso_map', None)
    if not mapping:
        return
    for principal, userid in mapping.items():
        print '%s\t%s' % (userid, principal)


def remove(args):
    root, closer = args.get_root(args.inst)
    users = find_users(root)
    mapping = getattr(users, 'sso_map', None)
    removed = False
    if mapping:
        if args.user in mapping:
            removed = True
            del mapping[args.user]
        else:
            for principal, userid in list(mapping.items()):
                if userid == args.user:
                    removed = True
                    del mapping[principal]
    if not removed:
        args.parser.error("No such user: %s" % args.user)
    transaction.commit()

