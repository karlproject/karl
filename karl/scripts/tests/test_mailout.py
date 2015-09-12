import mock
import unittest

from pyramid import testing


class MockQueueProcessor(object):
    @property
    def maildir(self):
        return iter(range(0, 10))

    _send_message = mock.MagicMock()


class Test_mailout(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()
        self.args = mock.MagicMock()
        self.env = dict(registry=DummyRegistry())
        self.mqp = MockQueueProcessor()

    def tearDown(self):
        testing.cleanUp()
        self.mqp._send_message.reset_mock()

    def fut(self):
        from karl.scripts.mailout import mailout
        return mailout

    def test_no_throttle(self):
        with mock.patch('repoze.sendmail.queue.QueueProcessor', return_value=self.mqp):
            self.fut()(self.args, self.env)
            self.assertEqual(self.mqp._send_message.call_count, 10)

    def test_no_throttle_second_call(self):
        with mock.patch('repoze.sendmail.queue.QueueProcessor', return_value=self.mqp):
            self.fut()(self.args, self.env)
            self.assertEqual(self.mqp._send_message.call_count, 10)

    def test_over_throttle(self):
        with mock.patch('repoze.sendmail.queue.QueueProcessor', return_value=self.mqp):
            self.env['registry'].mailout_throttle = 2
            self.fut()(self.args, self.env)
            self.assertEqual(self.mqp._send_message.call_count, 2)

    def test_under_throttle(self):
        with mock.patch('repoze.sendmail.queue.QueueProcessor', return_value=self.mqp):
            self.env['registry'].mailout_throttle = 12
            self.fut()(self.args, self.env)
            self.assertEqual(self.mqp._send_message.call_count, 10)


class DummyRegistry:
    def __init__(self):
        self.mailout_throttle = None

    @property
    def settings(self):
        return dict(
            mail_queue_path=None,
            mailout_throttle=self.mailout_throttle
        )
