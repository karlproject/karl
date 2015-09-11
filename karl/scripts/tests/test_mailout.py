import mock
import unittest

from pyramid import testing


class DummyQueueProcessor:
    def __init__(self, mailer, queue_path):
        self.mailer = mailer
        self.queue_path = queue_path
        self.dummy_output = []

    @property
    def maildir(self):
        return iter(range(0, 10))

    def _send_message(self, filename):
        self.dummy_output.append(filename)


class Test_mailout(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()
        self.fake_qp = DummyQueueProcessor(4, 5)
        self.patcher = mock.patch('repoze.sendmail.queue.QueueProcessor')
        self.MockClass = self.patcher.start()
        self.MockClass.return_value = self.fake_qp
        self.args = DummyArgs()
        self.env = dict(registry=DummyRegistry())

    def tearDown(self):
        self.MockClass.return_value = None
        self.patcher.stop()
        testing.cleanUp()

    def fut(self):
        from karl.scripts.mailout import mailout
        return mailout

    def test_mailout_no_throttle(self):
        self.fut()(self.args, self.env)
        self.assertEqual(len(self.fake_qp.dummy_output), 10)

    def test_mailout_throttle(self):
        # self.env['registry'].mailout_throttle = 2
        self.fut()(self.args, self.env)
        # self.assertEqual(len(self.fake_qp.dummy_output), 2)
        self.assertEqual(self.fake_qp.maildir, 99)


class DummyArgs:
    server = port = username = password = no_tls = force_tls = None


class DummyRegistry:
    def __init__(self):
        self.mailout_throttle = None

    @property
    def settings(self):
        return dict(
            mail_queue_path=None,
            mailout_throttle=self.mailout_throttle
        )
