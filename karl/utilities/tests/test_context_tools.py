import mock
import unittest


class TestContextTools(unittest.TestCase):

    @mock.patch('karl.utilities.context_tools.getMultiAdapter')
    @mock.patch('karl.utilities.context_tools.find_community')
    def test_it_in_community(self, find_community, getMultiAdapter):
        from karl.utilities.context_tools import context_tools
        from karl.models.interfaces import ICommunityInfo
        find_community.return_value = 'community'
        getMultiAdapter.return_value = tools = mock.Mock()
        tools.tabs = 'tabs'
        context, request = mock.Mock(), mock.Mock()
        self.assertEqual(context_tools(context, request), 'tabs')
        find_community.assert_called_once_with(context)
        getMultiAdapter.assert_called_once_with(
            ('community', request), ICommunityInfo)
