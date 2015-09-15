from datetime import date
from json import dump
from os import mkdir
from os.path import exists, join
import sys
import time

from repoze.sendmail.mailer import SMTPMailer
from repoze.sendmail.queue import QueueProcessor

from karl.scripting import create_karl_argparser
from karl.scripting import daemonize_function
from karl.scripting import only_one


class MailoutStats(object):
    def __init__(self, mailout_stats_dir=None):
        if mailout_stats_dir is not None and not exists(mailout_stats_dir):
            mkdir(mailout_stats_dir)
        self.mailout_stats_dir = mailout_stats_dir

    @property
    def today_dir(self):
        # Generate a subdirectory name with YYMMDD for today
        today = date.today().strftime("%Y%m%d")
        full_today = join(self.mailout_stats_dir, today)
        if not exists(full_today):
            mkdir(full_today)
        return full_today

    def _unpack_email(self, message):
        # Extract what's needed from the email message
        message_id = 'No value specified'
        message_id_count = 0
        for key, value in message.items():
            if key.lower() == 'message-id':
                message_id = value
                message_id_count += 1
        return {
            'From': message.get('From', 'No value specified'),
            'To': message.get('To', 'No value specified'),
            'Subject': message.get('Subject', 'No value specified'),
            'Message-Id': message_id,
            'message_id_count': message_id_count
        }

    def log(self, email, status):
        if self.mailout_stats_dir is None:
            return
        dump_data = self._unpack_email(email)
        dump_data['status'] = status
        fn = join(self.today_dir, dump_data.get('Message-Id', str(time.time())))
        with open(fn, 'w') as outfile:
            dump(dump_data, outfile, sort_keys=True, indent=4,
                 ensure_ascii=False)
        return fn

def mailout(args, env):
    registry = env['registry']

    queue_path = registry.settings['mail_queue_path']
    mailout_throttle = registry.settings.get('mailout_throttle')

    mailer = SMTPMailer(
        hostname=args.server,
        port=args.port,
        username=args.username,
        password=args.password,
        no_tls=args.no_tls,
        force_tls=args.force_tls
    )
    qp = QueueProcessor(mailer, queue_path)
    stats = MailoutStats(registry.settings.get('mailout_stats_dir'))

    # Instead of calling QueueProcessor.send_messages directly,
    # implement a throttle
    if mailout_throttle:
        int_mailout_throttle = int(mailout_throttle)
    else:
        int_mailout_throttle = 0
    counter = 0
    for filename in qp.maildir:
        counter += 1

        # Two cases, with and without the configuration setting. Let's
        # treat the separately, to be explicit instead of concise.

        if mailout_throttle is None:
            # No throttle, send
            qp._send_message(filename)
        else:
            # We do have a throttle, make sure we are under the counter
            if counter <= int_mailout_throttle:
                qp._send_message(filename)


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
        f = daemonize_function(mailout, args.interval)
        only_one(f, env['registry'], 'mailout')(args, env)
    else:
        only_one(mailout, env['registry'], 'mailout')(args, env)
