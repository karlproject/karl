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


class Test_mailout_stats(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()
        import tempfile
        self.temp_var = tempfile.gettempdir()
        from os.path import join
        self.temp_mailout_stats = join(self.temp_var, 'mailout_stats_dir')
        self._clean_dir()

    def _clean_dir(self):
        from shutil import rmtree
        from os.path import exists
        if exists(self.temp_mailout_stats):
            rmtree(self.temp_mailout_stats, True)

    def tearDown(self):
        testing.cleanUp()
        self._clean_dir()

    def fut(self):
        from karl.scripts.mailout import MailoutStats
        return MailoutStats

    def test_handles_existing_directory(self):
        from os import mkdir
        from os.path import exists
        mkdir(self.temp_mailout_stats)
        inst = self.fut()(self.temp_mailout_stats)
        self.assertEqual(self.temp_mailout_stats, inst.mailout_stats_dir)
        self.assertTrue(exists(inst.mailout_stats_dir))

    def test_handles_no_directory(self):
        from os.path import exists
        inst = self.fut()(self.temp_mailout_stats)
        self.assertEqual(self.temp_mailout_stats, inst.mailout_stats_dir)
        self.assertTrue(exists(inst.mailout_stats_dir))

    def test_handles_none_argument(self):
        inst = self.fut()(None)
        self.assertEqual(inst.mailout_stats_dir, None)

    def test_makes_today(self):
        from os.path import exists
        from os.path import join
        inst = self.fut()(self.temp_mailout_stats)
        from datetime import date
        today = date.today().strftime("%Y%m%d")
        full_today = join(self.temp_mailout_stats, today)
        self.assertEqual(inst.today_dir, full_today)
        self.assertTrue(exists(inst.today_dir))


class DummyRegistry:
    def __init__(self):
        self.mailout_throttle = None

    @property
    def settings(self):
        return dict(
            mail_queue_path=None,
            mailout_throttle=self.mailout_throttle
        )


def DummySettings(**kw):
    d = {}
    for k, v in kw.items():
        d[k] = v
    return d
