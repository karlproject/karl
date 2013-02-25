import os

if 'KARL_WEBTEST' in os.environ:
    from karl.webtests.base import Base


    class TestStatic(Base):
        """
        Basic smoke test, hits all screens in Karl and makes sure the templates
        render without raising an exception.
        """

        def test_static_with_no_path_is_not_found(self):
            from webtest import AppError
            with self.assertRaises(AppError) as cm:
                self.app.get('/static/')
            self.assertIn('404 Not Found', str(cm.exception))
