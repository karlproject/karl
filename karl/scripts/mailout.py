import sys

from repoze.sendmail.mailer import SMTPMailer
from repoze.sendmail.queue import QueueProcessor

from karl.scripting import create_karl_argparser
from karl.scripting import daemonize_function

def mailout(args, env):

    registry = env['registry']

    queue_path = registry.settings['mail_queue_path']

    mailer = SMTPMailer(
        hostname=args.server,
        port=args.port,
        username=args.username,
        password=args.password,
        no_tls=args.no_tls,
        force_tls=args.force_tls
    )
    qp = QueueProcessor(mailer, queue_path)
    qp.send_messages()

def main(argv=sys.argv):
    default_interval = 300

    parser = create_karl_argparser(description='Send outgoing mail.')
    parser.add_argument('--server', '-s', default="localhost", metavar='HOST',
                        help='SMTP server host name.  Default is localhost.', )
    parser.add_argument('--port', '-P', type=int, default=25, metavar='PORT',
                        help='Port of SMTP server.  Default is 25.', )
    parser.add_argument('--username', '-u',
                        help='Username, if authentication is required')
    parser.add_argument('--password', '-p',
                        help='Password, if authentication is required')
    parser.add_argument('--force-tls', '-f', action='store_true',
                        help='Require that TLS be used.')
    parser.add_argument('--no-tls', '-n', action='store_true',
                        help='Require that TLS not be used.')
    parser.add_argument('-d', '--daemon', action='store_true',
                        help="Run in daemon mode.")
    parser.add_argument('-i', '--interval', type=int, default=default_interval,
                        help="Interval in seconds between executions in "
                        "daemon mode.  Default is %d." % default_interval)

    args = parser.parse_args(sys.argv[1:])

    env = args.bootstrap(args.config_uri)

    if args.daemon:
        daemonize_function(mailout, args.interval)(args, env)
    else:
        mailout(args, env)

