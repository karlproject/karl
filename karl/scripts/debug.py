from code import interact
import sys

from karl.scripting import create_karl_argparser

def main(argv=sys.argv):
    parser =  create_karl_argparser(
        description='Open a debug session with a Karl instance.'
        )
    parser.add_argument('-S', '--script', default=None,
                        help='Script to run. If not specified will start '
                        'an interactive session.')
    args = parser.parse_args(argv[1:])
    env = args.bootstrap(args.config_uri)
    root, closer = env['root'], env['closer']
    cprt = ('Type "help" for more information. "app" is the karl Pyramid '
            'application.')
    script = args.script
    if script is None:
        banner = "Python %s on %s\n%s" % (sys.version, sys.platform, cprt)
        interact(banner, local=env)
    else:
        code = compile(open(script).read(), script, 'exec')
        exec code in env
