
import datetime
import random

from pyramid.security import effective_principals
from pyramid.security import authenticated_userid
from zope.component import getMultiAdapter

from karl.models.interfaces import IGridEntryInfo
from karl.models.interfaces import ICommunityContent
from karl.models.interfaces import ICommunityInfo
from karl.utils import find_communities
from karl.utils import find_community
from karl.utils import find_profiles
from karl.views.batch import get_catalog_batch
from karl.views.communities import get_my_communities
from karl.views.chatter import followed_chatter_json
from karl.views.chatter import TIMEAGO_FORMAT
from karl.views.chatter import direct_messages_json


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
    # XXX do a real query from here, using updates[name] for start date.
    notifications['radar'] = dict(
        cnt = random.choice([0, random.randrange(1, 5)]),
        ts = now_iso,
        )
    # chatter recent
    profiles = find_profiles(request.context)
    userid = authenticated_userid(request)
    profile = profiles.get(userid)
    request.GET['since'] = profile.last_chatter_query.strftime(TIMEAGO_FORMAT)
    followed_chatter = followed_chatter_json(context, request)
    recent = followed_chatter['recent']
    notifications['chatter'] = dict(
        cnt = len(recent),
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
    results['partials'] = {
        'chatter_post_partial': layout.microtemplates['chatter_post_partial']
        }
    # Sometimes there is no need for an update. The server can just return
    # empty data. A condition is that a ts parameter is sent to us. The
    # other condition (does the client need an update?) is now simulated
    # with a random choice.
    all_chatter = followed_chatter_json(context, request)
    all_chatter_len = len(all_chatter['recent'])
    private_chatter = direct_messages_json(context, request)
    private_chatter_len = len(private_chatter['messages'])
    total_chatter_len = all_chatter_len + private_chatter_len
    if ts_iso and total_chatter_len == 0:
        results['data'] = None
    else:
        results['data'] = {
            'chatter_url': layout.chatter_url,
            'streams': [],
        }
        all_chatter_stream = {
            'class': 'recent-friend',
            'title': 'Posts',
            'private': False,
            'has_more_news': all_chatter_len > 5 and (all_chatter_len - 5) or 0,
            'has_more_news_url': layout.chatter_url,
            'thisUrl': request.params.get('thisURL', request.url),
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
            'title': 'Messages',
            'private': True,
            'has_more_news': private_chatter_len > 5 and (private_chatter_len - 5) or 0,
            'has_more_news_url': '%sdirect.html' % layout.chatter_url,
            'thisUrl': request.params.get('thisURL', request.url),
            'items': [
                {
                    'author': item['creator'],
                    'author_profile_url': item['creator_url'],
                    'message_url': item['url'],
                    'image_url': item['creator_image_url'],
                    'text': item['text'],
                    'info': item['timeago'],
                    'new': False,
                } for item in private_chatter['messages'][:5]
            ],
        }
        results['data']['streams'].append(all_chatter_stream)
        results['data']['streams'].append(private_chatter_stream)
    profiles = find_profiles(request.context)
    userid = authenticated_userid(request)
    profile = profiles.get(userid)
    if profile is not None:
        profile.last_chatter_query = datetime.datetime.utcnow()
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
        results['partials'] = []
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
        communities_info = [
            dict(
                title=community.title,
                description=community.description,
                url=community.url,
                actions=[dict(
                    url=community.url + (a_name if a_name != 'overview' else 'view.html'),
                    title=a_name.capitalize(),
                    last=a_name == 'files',
                    ) for a_name in ('overview', 'blog', 'calendar', 'files', 'wiki')],
            )
            for community in communities[:5]
        ]

        # 3rd column: My Recent Activity
        recent_items = []
        recent_items_batch = get_catalog_batch(context, request, batch_size=5,
            interfaces=[ICommunityContent], sort_index="modified_date",
            reverse=True, modified_by=authenticated_userid(request),
            allowed={'query': effective_principals(request), 'operator': 'or'})

        for item in recent_items_batch["entries"]:
            adapted = getMultiAdapter((item, request), IGridEntryInfo)
            community = find_community(item)
            if community is not None:
                community_adapter = getMultiAdapter((community, request), ICommunityInfo)
                community_info = dict(
                    url=community_adapter.url,
                    title=community_adapter.title,
                )
            else:
                community_info = None
            # Since this is json, we need a real dict...
            recent_items.append(dict(
                title=adapted.title,
                url=adapted.url,
                modified=adapted.modified,
                creator_title=adapted.creator_title,
                type=adapted.type,
                community=community_info,
                ))

        # Provide fake "approval items" for the "approvals" tab.

        approval_waitinglist_items = [{
            'title': 'Approval Waiting List',
            'group': [{
                'title': 'e-Payment',
                'count': 0,
                'id': 'table1'
                }, {
                'title': 'Grant Payment',
                'count': 2,
                'id': 'table2'
                }, {
                'title': 'Contract Review',
                'count': 3,
                }, {
                'title': 'Contract Approval',
                'count': 2,
                }, {
                'title': 'Contract Payment',
                'count': 1,
                }, {
                'title': 'Hardware / Software Request',
                'count': 4,
                }
            ]
        }, {
            'title': 'Payment Waiting List',
            'group': [{
                'title': 'e-Payment',
                'count': 0,
                }, {
                'title': 'Grant Payment',
                'count': 133,
                }, {
                'title': 'Contract Payment',
                'count': 116,
                }
            ]
        }, {
            'title': 'Accrual Waiting List',
            'group': [{
                'title': 'Grant Accrual',
                'count': 7,
                }
            ]

        }, {
            'title': 'Fixed Assets Waiting List',
            'group': [{
                'title': 'e-Approval',
                'count': 7,
                }, {
                'title': 'e-Bridge for Posting',
                'count': 3,
                }
            ]

        }];


        approval_table1_items = [{
            'amt': '45.09',
            'via': 'Check',
            'approvedBy': 'Some Person',
            'status': 'Approved',
            'statusDate': '02/09/2012',
            'overdueBy': '13',
            }, {
            'amt': '13.00',
            'via': 'Wire',
            'approvedBy': 'Another Person',
            'status': 'Submitted',
            'statusDate': '02/14/2012',
            'overdueBy': '16',
            }, {
            'amt': '71.21',
            'via': 'Check',
            'approvedBy': 'Last Person',
            'status': 'Approved',
            'statusDate': '02/13/2012',
            'overdueBy': '18',
            }]

        for i, row in enumerate(approval_table1_items):
            row['rowClass'] = 'even' if i % 2 else 'odd'

        import copy
        approval_table2_items = 2 * copy.deepcopy(approval_table1_items)
        for i, row in enumerate(approval_table2_items):
            row['rowClass'] = 'even' if i % 2 else 'odd'

        # Assemble the final result.
        results['data'] = {
            # home section
            'home': [{
                'class': 'homepanel1',
                'title': 'My Communities',
                'communities': communities_info,
                }, {
                'class': 'homepanel2',
                'title': 'My Recent Activity',
                'contexts': recent_items,
                }],
            # approvals section
            'approvals': [{
                'class': 'approvalpanel1',
                'waitinglist': {
                    'items': approval_waitinglist_items,
                    },
                }, {
                'class': 'approvalpanel2',
                'tables': [{
                    'id': 'table1',
                    'title': 'Open Project Project',
                    'items': approval_table1_items,
                    }, {
                    'id': 'table2',
                    'title': 'Very Open Project',
                    'items': approval_table2_items,
                    }],
                }],
            }

        results['state'] = {
            'chart1': {
                'options' : {
                    'title': 'Company Performance',
                    'hAxis': {
                        'title': 'Year',
                        'titleTextStyle': {'color': 'red'},
                        },
                    'width': 200,      # Must have fixed width! (matching css)
                    },
                'columns': [
                    ['string', 'Year'],
                    ['number', 'Sales'],
                    ['number', 'Expenses'],
                    ],
                'rows': [
                    ['2004', 1000, 400],
                    ['2005', 1170, 460],
                    ['2006', 660, 1120],
                    ['2007', 1030, 540],
                    ],
                },
            'chart2': {
                'options' : {
                    'title': 'Monthly Operating Revenue',
                    'hAxis': {
                        'title': 'Project',
                        'titleTextStyle': {'color': 'red'},
                        },
                    'width': 400,      # Must have fixed width! (matching css)
                    },
                'columns': [
                    ['string', 'Project'],
                    ['number', 'Budgeted'],
                    ['number', 'Actual'],
                    ],
                'rows': [
                    ['My First Project', 1000, 400],
                    ['Another Project', 1170, 460],
                    ['A Third Project', 660, 1120],
                    ],
                },
            }


    return results

