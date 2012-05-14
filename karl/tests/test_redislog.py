import mock
import unittest


class TestRedisLog(unittest.TestCase):

    def setUp(self):
        self.redis = DummyRedis()
        self.redis_patch = mock.patch('karl.redislog.redis', self.redis)
        self.redis_patch.start()

    def tearDown(self):
        self.redis_patch.stop()

    def make_one(self):
        from karl.redislog import RedisLog as test_class
        return test_class()

    def populate(self, log):
        i = 0
        for j in xrange(0, 4):
            for level in ("DEBUG", "INFO"):
                for category in ("webapp", "mailin"):
                    i += 1
                    log.log(level, category, str(i))

    def test_log(self):
        log = self.make_one()
        log.log('INFO', 'test', 'My name is Test.')
        entry = list(log.iterate())[0]
        self.assertEqual(entry.level, 'INFO')
        self.assertEqual(entry.category, 'test')
        self.assertEqual(entry.message, 'My name is Test.')
        self.assertEqual(entry.traceback, None)

    def test_error(self):
        import logging
        log = self.make_one()
        try:
            raise Exception("Something went wrong.")
        except:
            log.log(logging.ERROR, 'test', 'Oh no!', True)
        entry = list(log.iterate())[0]
        self.assertEqual(entry.level, 'ERROR')
        self.assertEqual(entry.category, 'test')
        self.assertEqual(entry.message, 'Oh no!')
        self.assertTrue('Something went wrong.' in entry.traceback)
        self.assertTrue('test_redislog.py' in entry.traceback)

    def test_iterate_all(self):
        log = self.make_one()
        self.populate(log)
        result = [int(e.message) for e in log.iterate()]
        self.assertEqual(result, [16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5,
                                  4, 3, 2, 1])
    def test_iterate_level(self):
        log = self.make_one()
        self.populate(log)
        result = [int(e.message) for e in log.iterate(level="DEBUG")]
        self.assertEqual(result, [14, 13, 10, 9, 6, 5, 2, 1])
        result = [int(e.message) for e in log.iterate(level="INFO")]
        self.assertEqual(result, [16, 15, 12, 11, 8, 7, 4, 3])

    def test_iterate_category(self):
        log = self.make_one()
        self.populate(log)
        result = [int(e.message) for e in log.iterate(category="webapp")]
        self.assertEqual(result, [15, 13, 11, 9, 7, 5, 3, 1])
        result = [int(e.message) for e in log.iterate(category="mailin")]
        self.assertEqual(result, [16, 14, 12, 10, 8, 6, 4, 2])

    def test_iterate_level_and_category(self):
        log = self.make_one()
        self.populate(log)
        result = [int(e.message) for e in log.iterate(level="DEBUG",
                                                      category="webapp")]
        self.assertEqual(result, [13, 9, 5, 1])

    def test_iterate_empty(self):
        log = self.make_one()
        self.assertEqual(list(log.iterate()), [])

    def test_iterate_missing_entries(self):
        log = self.make_one()
        self.populate(log)
        del self.redis._db[self.redis._inserts[0]]
        result = [int(e.message) for e in log.iterate()]
        self.assertEqual(result, [16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4,
                                  3, 2])

class DummyRedis(object):

    @property
    def StrictRedis(self):
        return self

    def __init__(self):
        self._db = {}
        self._inserts = []

    def __call__(self, **kw):
        self.__dict__.update(kw)
        return self

    def get(self, key):
        return self._db.get(key)

    def getset(self, key, value):
        prev = self._db.get(key)
        self._db[key] = value
        return prev

    def setex(self, key, ttl, value):
        self._db[key] = value
        self._inserts.append(key)

    def pipeline(redis):
        class DummyPipeline(object):
            def __init__(self):
                self.answers = []

            def getset(self, key, value):
                self.answers.append(redis.getset(key, value))

            def execute(self):
                return self.answers

        return DummyPipeline()
