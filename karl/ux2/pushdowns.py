
import datetime
import random
import itertools

from zope.component import getMultiAdapter

from karl.models.interfaces import IGridEntryInfo
from karl.utils import find_communities
from karl.views.communities import get_my_communities
from karl.views.community import get_recent_items_batch
from karl.views.chatter import followed_chatter_json


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
        all_chatter = followed_chatter_json(context, request)
        all_chatter_len = len(all_chatter['recent'])
        results['data'] = {
            'chatter_url': layout.chatter_url,
            'streams': [],
        }
        all_chatter_stream = {
            'class': 'recent-friend',
            'title': 'Friends activity',
            'has_more_news': all_chatter_len > 5 and (all_chatter_len - 5) or 0,
            'has_more_news_url': layout.chatter_url,
            'items': [
                {
                    'author': item['creator'],
                    'author_profile_url': item['creator_url'],
                    'message_url': item['url'],
                    'image_url': item['creator_image_url'],
                    'text': item['text'],
                    'info': item['timeago'],
                    'new': True,
                } for item in all_chatter['recent'][:5]
            ],
        }
        private_chatter_stream = {
            'class': 'your-stream',
            'title': 'Direct messages',
            'has_more_news': all_chatter_len > 5 and (all_chatter_len - 5) or 0,
            'has_more_news_url': '%sdirect.html' % layout.chatter_url,
            'items': [
                {
                    'author': item['creator'],
                    'author_profile_url': item['creator_url'],
                    'message_url': item['url'],
                    'image_url': item['creator_image_url'],
                    'text': item['text'],
                    'info': item['timeago'],
                    'new': False,
                } for item in all_chatter['recent'][:5]
            ],
        }
        results['data']['streams'].append(all_chatter_stream)
        results['data']['streams'].append(private_chatter_stream)
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

