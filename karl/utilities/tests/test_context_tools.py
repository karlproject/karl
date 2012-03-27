import mock
import unittest

from pyramid import testing


class TestContextTools(unittest.TestCase):

    @mock.patch('karl.utilities.context_tools.getMultiAdapter')
    @mock.patch('karl.utilities.context_tools.find_community')
    def test_it_in_community(self, find_community, getMultiAdapter):
        from karl.utilities.context_tools import context_tools
        from karl.models.interfaces import ICommunityInfo
        community = testing.DummyResource()
        community['members'] = testing.DummyResource()
        community['foo'] = context = testing.DummyResource()
        find_community.return_value = community
        getMultiAdapter.return_value = tools = mock.Mock()
        tools.tabs = ['tabs']
        request = mock.Mock()
        request.resource_url.return_value = 'members_url'
        tools = context_tools(context, request)
        self.assertEqual(len(tools), 2)
        self.assertEqual(tools[0], 'tabs')
        self.assertEqual(tools[1],{
            'url': 'members_url', 'selected': False,
            'name': 'members', 'title': 'Members'})
        find_community.assert_called_once_with(context)
        getMultiAdapter.assert_called_once_with(
            (community, request), ICommunityInfo)
        request.resource_url.assert_called_once_with(community['members'])


    @mock.patch('karl.utilities.context_tools.find_community')
    def test_it_no_community(self, find_community):
        from karl.utilities.context_tools import context_tools
        find_community.return_value = None
        self.assertEqual(context_tools(None, None), None)
