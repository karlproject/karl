import argparse
from code import interact
import sys

from pyramid.paster import bootstrap

from karl.scripting import get_default_config

def main(argv=sys.argv):
    parser =  argparse.ArgumentParser(
        description='Open a debug session with a Karl instance.'
        )
    parser.add_argument(
        '-C', '--config',
        metavar='FILE',
        default=None,
        dest='config_uri',
        help='Path to configuration ini file (defaults to $CWD/etc/karl.ini).'
        )
    parser.add_argument('-S', '--script', default=None,
                        help='Script to run. If not specified will start '
                        'an interactive session.')
    args = parser.parse_args(argv[1:])
    config_uri = args.config_uri
    if config_uri is None:
        config_uri = get_default_config()
    env = bootstrap(config_uri)
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
