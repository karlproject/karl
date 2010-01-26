import unittest

class TestLog(unittest.TestCase):
    def setUp(self):
        import karl.log
        self.logging_module = karl.log.logging
        karl.log.logging = self.log = DummyLoggingModule()

    def tearDown(self):
        import karl.log
        karl.log.logging = self.logging_module

    def test_no_setup(self):
        from karl.log import get_logger
        from karl.log import NullHandler
        logger = get_logger()
        self.assertEqual(len(logger.handlers), 1)
        self.failUnless(isinstance(logger.handlers[0], NullHandler))

class DummyLoggingModule(object):
    level = None

    def __init__(self):
        self.handlers = []

    def addHandler(self, handler):
        self.handlers.append(handler)

    def removeHandler(self, handler):
        self.handlers.remove(handler)

    def getLogger(self, name):
        return self

    def setLevel(self, level):
        self.level = level
