
import datetime
import random
import itertools

from zope.component import getMultiAdapter

from karl.models.interfaces import IGridEntryInfo
from karl.utils import find_communities
from karl.views.communities import get_my_communities
from karl.views.community import get_recent_items_batch


def notifier_ajax_view(context, request):
    # Example result set, for demonstrating without
    # a real server database.
    
    # XXX This method should dispatch a call to each catalog
    # search that needs to be notified.
    # It only needs to provide the recent counters in the resulting payload.

    # The request contains parameters for each notification source, keyed
    # by their name. The value is a date which contains the end of the last
    # succesful query.

    updates = {}
    for name, value in request.params.iteritems():
        # value is in isodate format, let's convert it to a real datetime.
        d = datetime.datetime.strptime(value.split('.')[0], '%Y-%m-%dT%H:%M:%S')
        updates[name] = d
    # ... for example update['chatter'] now contains the start-date that the
    # chatter query will need.
    
    now = datetime.datetime.now()
    now_iso = now.isoformat()
    # Only those pushdowns are notified, who are in the dictionary.
    notifications = {}
    for name in ['chatter', 'radar']:
        # XXX do a real query from here, using updates[name] for start date.
        notifications[name] = dict(
            cnt = random.choice([0, random.randrange(1, 5)]),
            ts = now_iso, 
            )

    return notifications


def chatter_ajax_view(context, request):
    # Example result set, for demonstrating the widget without
    # a real server database.
    results = {}
    # Datetime of the current search. (The client will pass it back
    # to us the next time, and we can decide if an update is needed)
    now = datetime.datetime.now()
    now_iso = now.isoformat()
    results['ts'] = now_iso
    ts_iso = request.params.get('ts', '')
    # template provision
    layout = request.layout_manager.layout
    if request.params.get('needsTemplate', 'false') in ('true', 'True'):
        # We need the template. So, let's fetch it.
        results['microtemplate'] = layout.microtemplates['chatter']
    # Sometimes there is no need for an update. The server can just return
    # empty data. A condition is that a ts parameter is sent to us. The
    # other condition (does the client need an update?) is now simulated
    # with a random choice.
    if ts_iso and random.choice([False, True]):
        results['data'] = None
    else:
        # Fetch the data
        results['data'] = {
            'chatter_url': layout.chatter_url,
            'streams': [{
                'class': 'your-stream',
                'title': 'Direct messages',
                'has_more_news': False,
                'items': [{
                        'author': 'Tester Testerson',
                        'author_profile_url': '#author_profile',
                        'message_url': '#message',
                        'image_url': 'http://twimg0-a.akamaihd.net/profile_images/413225762/python_normal.png',
                        'text': 'Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at ve.',
                        'info': '3 min ago',
                        'new': True,
                    }, {
                        'author': 'Tester Testerson',
                        'author_profile_url': '#author_profile',
                        'message_url': '#message',
                        'image_url': 'http://twimg0-a.akamaihd.net/profile_images/413225762/python_normal.png',
                        'text': 'Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at ve.',
                        'info': '4 min ago',
                        'new': False,
                    }, {
                        'author': 'John Doe',
                        'author_profile_url': '#author_profile',
                        'message_url': '#message',
                        'image_url': 'http://twimg0-a.akamaihd.net/profile_images/413225762/python_normal.png',
                        'text': 'Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volu',
                        'info': '5 min ago',
                        'new': False,
                    }, {
                        'author': 'Tester Testerson',
                        'author_profile_url': '#author_profile',
                        'message_url': '#message',
                        'image_url': 'http://twimg0-a.akamaihd.net/profile_images/413225762/python_normal.png',
                        'text': 'Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at ve.',
                        'info': '4 min ago',
                        'new': False,
                    }],
                }, {
                'class': 'recent-friend',
                'title': 'Friends activity',
                'has_more_news': True,
                'items': [{
                        'author': 'John Doe',
                        'author_profile_url': '#author_profile',
                        'message_url': '#message',
                        'image_url': 'http://twimg0-a.akamaihd.net/profile_images/413225762/python_normal.png',
                        'text': 'Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volu',
                        'info': '3 min ago',
                        'new': True,
                    }, {
                        'author': 'Tester Testerson',
                        'author_profile_url': '#author_profile',
                        'message_url': '#message',
                        'image_url': 'http://twimg0-a.akamaihd.net/profile_images/413225762/python_normal.png',
                        'text': 'Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volu',
                        'info': '4 min ago',
                        'new': True,
                    }, {
                        'author': 'Tester Testerson',
                        'author_profile_url': '#author_profile',
                        'message_url': '#message',
                        'image_url': 'http://twimg0-a.akamaihd.net/profile_images/413225762/python_normal.png',
                        'text': 'Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at ve.',
                        'info': '4 min ago',
                        'new': True,
                    }, {
                        'author': 'John Doe',
                        'author_profile_url': '#author_profile',
                        'message_url': '#message',
                        'image_url': 'http://twimg0-a.akamaihd.net/profile_images/413225762/python_normal.png',
                        'text': 'Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volu',
                        'info': '5 min ago',
                        'new': True,
                    }],
                }],
            }
    return results


def radar_ajax_view(context, request):
    # Example result set, for demonstrating the widget without
    # a real server database.
    results = {}
    # Datetime of the current search. (The client will pass it back
    # to us the next time, and we can decide if an update is needed)
    now = datetime.datetime.now()
    now_iso = now.isoformat()
    results['ts'] = now_iso
    ts_iso = request.params.get('ts', '')
    # template provision
    if request.params.get('needsTemplate', 'false') in ('true', 'True'):
        # We need the template. So, let's fetch it.
        layout = request.layout_manager.layout
        results['microtemplate'] = layout.microtemplates['radar']
    # Sometimes there is no need for an update. The server can just return
    # empty data. A condition is that a ts parameter is sent to us. The
    # other condition (does the client need an update?) is now simulated
    # with a random choice.
    if ts_iso and random.choice([False, True]):
        results['data'] = None
    else:
        # Fetch the data

        # 2nd column: my communities (preferred communities)
        communities_folder = find_communities(context)
        communities = get_my_communities(communities_folder, request)
        communities_info = ((
            dict(
                title=community.title,
                description=community.description,
                url=community.url,
            )
            for community in communities
        ))
        communities_info = list(itertools.islice(communities_info, 0, 5))

        # 3rd column: My Recent Activity
        recent_items = []
        recent_items_batch = get_recent_items_batch(context, request, size=5)
        for item in recent_items_batch["entries"]:
            adapted = getMultiAdapter((item, request), IGridEntryInfo)
            # Since this is json, we need a real dict...
            recent_items.append(dict(
                title=adapted.title,
                url=adapted.url,
                modified=adapted.modified,
                creator_title=adapted.creator_title,
                type=adapted.type,
                ))

        results['data'] = {
            'streams': [{
                'class': 'stream1',
                'title': 'My Communities',
                'communities': communities_info,
                }, {
                'class': 'stream2',
                'title': 'My Recent Activity',
                'contexts': recent_items,
                }],
            }

    return results

