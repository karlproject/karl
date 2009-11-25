# Copyright (C) 2008-2009 Open Society Institute
#               Thomas Moroz: tmoroz@sorosny.org
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License Version 2 as published
# by the Free Software Foundation.  You may not use, modify or distribute
# this program under any other version of the GNU General Public License.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

"""
Generate some statistics about usage.
"""

import datetime
from optparse import OptionParser

from csv import DictWriter
import logging
import sys
import transaction

from repoze.folder.interfaces import IFolder
from karl.models.interfaces import ICommunity
from karl.models.interfaces import IComment
from karl.models.interfaces import IProfile
from karl.content.interfaces import IWikiPage
from karl.content.interfaces import IBlogEntry
from karl.content.interfaces import ICalendarEvent
from karl.content.interfaces import ICommunityFile

from karl.scripting import get_default_config
from karl.scripting import open_root

from karl.utils import find_tags
from karl.utils import find_users

log = logging.getLogger(__name__)

def walk(startnode, visit, leave):
    """Visit shallow nodes earlier."""
    def traverse(node):
        sys.stdout.write('.'); sys.stdout.flush()
        visit(node)
        if IFolder.providedBy(node):
            for child in node.values():
                traverse(child)
        leave(node)

        if hasattr(node, '_p_deactivate'):
            # attempt to not run out of memory
            node._p_deactivate()

    return traverse(startnode)

def is_private(context):
    return getattr(context, 'security_state', None) == 'private'

def last_activity(community):
    pass # XXX

class CommunitiesReport(object):
    filename = 'communities.csv'

    columns = [
        'community',
        'id',
        'is_private',
        'members',
        'moderators',
        'last_activity',
        'create_date',
        'wiki_pages',
        'blog_entries',
        'blog_comments',
        'files',
        'calendar_events',
        'community_tags',
        'hits_this_month',
        'percent_engaged',
        ]

    def __init__(self):
        self.rows = []
        self.row = None
        self.community = None

    def visit(self, context):
        if ICommunity.providedBy(context):
            self.community = context
            self.row = {
                'community': context.title,
                'id': context.__name__,
                'is_private': is_private(context),
                'members': len(context.member_names),
                'moderators': len(context.moderator_names),
                'last_activity': context.content_modified,
                'create_date': context.created,
                'wiki_pages': 0,
                'blog_entries': 0,
                'blog_comments': 0,
                'files': 0,
                'calendar_events': 0,
                'community_tags': set(),
                'hits_this_month': 'Unknown',
                'percent_engaged': 'Unknown'
                }

        elif self.community is None:
            return

        else:
            last_activity = getattr(context, 'content_modified', None)
            if (last_activity is not None and
                last_activity > self.row['last_activity']):
                self.row['last_activity'] = last_activity

        if IWikiPage.providedBy(context):
            self.row['wiki_pages'] += 1
        elif IBlogEntry.providedBy(context):
            self.row['blog_entries'] += 1
        elif IComment.providedBy(context):
            self.row['blog_comments'] += 1
        elif ICommunityFile.providedBy(context):
            self.row['files'] += 1
        elif ICalendarEvent.providedBy(context):
            self.row['calendar_events'] += 1

        tags = find_tags(context)
        docid = getattr(context, 'docid', None)
        if docid is not None:
            for tag in tags.getTags([docid,]):
                self.row['community_tags'].add(tag)

    def leave(self, context):
        if ICommunity.providedBy(context):
            assert context is self.community
            self.row['community_tags'] = len(self.row['community_tags'])
            self.rows.append(self.row)
            self.row = self.community = None

class PeopleReport(object):
    filename = 'people.csv'
    columns = [
        'first_last',
        'profile_id',
        'create_date',
        'is_staff',
        'membership',
        'communities_moderator',
        'location',
        'department',
        'content_created',
        'tags',
        'created_this_month',
    ]

    def __init__(self):
        self.people = {}
        self.one_month_ago = (datetime.datetime.now() -
                              datetime.timedelta(days=30))

    @property
    def rows(self):
        r = list(self.people.values())
        r.sort(key=lambda x: x['profile_id'])
        return r

    def _get_person(self, id):
        if id not in self.people:
            self.people[id] = {
                'first_last': None,
                'profile_id': id,
                'create_date': None,
                'is_staff': None,
                'membership': 0,
                'communities_moderator': 0,
                'location': None,
                'department': None,
                'content_created': 0,
                'tags': None,
                'created_this_month': 0,
                }

        return self.people[id]

    def visit(self, context):
        if IProfile.providedBy(context):
            users = find_users(context)
            person = self._get_person(context.__name__)
            person['first_last'] = ' '.join(
                (context.firstname, context.lastname))
            person['create_date'] = context.created
            person['is_staff'] = users.member_of_group(
                context.__name__, 'group.KarlStaff')
            person['location'] = context.location
            person['department'] = context.department

            tags = find_tags(context)
            person['tags'] = len(tags.getTags(users=[context.__name__]))

        elif ICommunity.providedBy(context):
            for id in context.member_names:
                self._get_person(id)['membership'] += 1
            for id in context.moderator_names:
                self._get_person(id)['communities_moderator'] += 1

        else:
            creator = getattr(context, 'creator', None)
            if creator is not None:
                person = self._get_person(creator)
                person['content_created'] += 1
                if context.created > self.one_month_ago:
                    person['created_this_month'] += 1

    def leave(self, context):
        pass

def gen_stats(root):
    reports = [
        CommunitiesReport(),
        PeopleReport(),
        ]
    def visit(context):
        for report in reports:
            report.visit(context)

    def leave(context):
        for report in reports:
            report.leave(context)

    walk(root, visit, leave)
    print ''

    for report in reports:
        write_report(report)

def write_report(report):
    f = open(report.filename, 'wb')
    print >>f, ','.join(report.columns)
    writer = DictWriter(f, report.columns)
    for row in report.rows:
        writer.writerow(_encode_row(row))
    f.close()

def _encode_row(row):
    new_row = {}
    for k,v in row.items():
        if isinstance(v, unicode):
            v = v.encode('utf-8')
        new_row[k] = v
    return new_row

def main(argv=sys.argv):
    logging.basicConfig()
    log.setLevel(logging.INFO)

    parser = OptionParser(
        description="Generate some statistics about Karl usage",
        usage="%prog [options]",
        )

    parser.add_option('-C', '--config', dest='config', default=None,
        help="Specify a paster config file. Defaults to $CWD/etc/karl.ini")
    options, args = parser.parse_args()

    if len(args):
        parser.error("Command does not take arguments.")

    config = options.config
    if not config:
        config = get_default_config()
    root, closer = open_root(config)

    try:
        gen_stats(root)
    finally:
        transaction.abort()

if __name__ == '__main__':
    main()
