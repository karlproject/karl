import mock
import unittest


class TestAddRendererGlobals(unittest.TestCase):

    def test_it(self):
        from karl.utilities.interfaces import IContextTools
        from karl.ux2.subscribers import add_renderer_globals
        context, request = mock.Mock(), mock.Mock()
        event = {'context': context, 'request': request}
        factory = request.registry.getUtility.return_value
        factory.return_value = 'Tools!!'
        add_renderer_globals(event)
        self.assertEqual(event['context_tools'], 'Tools!!')
        request.registry.getUtility.assert_called_once_with(IContextTools)
        factory.assert_called_once_with(context, request)
