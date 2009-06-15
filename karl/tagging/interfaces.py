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

from zope.interface import Interface
from zope.schema import Datetime
from zope.schema import Int
from zope.schema import Set
from zope.schema import TextLine

class ITag(Interface):
    """ Scehma for a single tag.
    """
    item = Int(
        title=u'Item',
        description=u'The item that is tagged.',
        required=True)

    user = TextLine(
        title=u'User',
        description=u'The user id that created the tag.',
        required=True)

    name = TextLine(
        title=u'Tag Name',
        description=u'The tag name the user provided for the item.',
        required=True)

    community = TextLine(
        title=u'Community',
        description=u'The name of the community containing the item, if any.',
        required=False,
        default=None)


class ITaggingEngine(Interface):
    """Manangement and Querying of Tags.

    Tags are small stickers that are specific to an object to be tageed and
    the user tagging the object.
    """

    def getTagsWithPrefix(prefix):
        """ Return all tags which start with 'prefix'.
        """

    def getTags(items=None, users=None, community=None):
        """ Look up tag string matching the specified items and users.

        o If 'items' is None, match all items

        o If 'users' is None, match all users.

        o If 'community' is not None, return only tags relevant to items
          in the given community.

        o The method returns a set of *normalized* tag names (unicode).
        """

    def getTagObjects(self, items, users, community=None):
        """ Look up tag objects matching the specified items and users.

        o If 'items' is None, match all items

        o If 'users' is None, match all users.

        o If 'community' is not None, return only tags relevant to items
          in the given community.

        o Return a set of objects implementing ITag.
        """

    def getCloud(items=None, users=None, community=None):
        """ Look up a set of tuples in the form of ('tag', frequency).

        o If 'items' is None, match all items

        o If 'users' is None, match all users.

        o If 'community' is not None, returned tuples match only tags
          relevant to items in the given community;  likewise, frequencies
          are only of items with the tag within that community.
        """

    def getItems(tags=None, users=None, community=None):
        """ Look up all items matching the specified tags and users.

        o If 'tags' is None, match all tags.

        o If 'users' is None, match all users.

        o If 'community' is not None, return only items within the
          given community.

        o Return a set of item ids (integer docids).
        """

    def getUsers(tags=None, items=None, community=None):
        """ Look up all users matching the specified tags and items.

        o If 'tags' is None, match all tags.

        o If 'items' is None, match all items

        o If 'community' is not None, return only users who have matching
          tags on items within the given community.

        o Return a set of strings (login names).
        """

    def getRelatedTags(tag, degree=1, community=None, user=None):
        """ Look up tags related to a given tag.

        o 'tag' is the source tag.

        o If 'community' is not None, restrict matches to tags on items
          within the given community.

        o If 'user' is not None, restrict matches to tags on items
          tagged by the given user.

        o 'degree' specifies the search depth.
        """

    def getRelatedItems(item, community=None, user=None):
        """ Look up a list of items related to a given item

        o Items are related if they have a least one tag in common with
          `item`.

        o If 'community' is not None, restrict matches to tags on items
          within the given community.

        o If 'user' is not None, restrict matches to tags on items
          tagged by the given user.

        o Return a list of tuples in the form (item, numTags), where
          'numTags' is the number of tags in common.

        o Sort the result in descending order by the numTags.
        """

    def getRelatedUsers(user, community=None):
        """ Look up a list of users related a given user.

        o Users are related if they have a least one tag in common with
          `user`.

        o Returna list of tuples in the form (user, numTags), where
          numTags is the number of tags in common.

        o Sort the result in descending order by the numTags.
        """

    def getFrequency(tags=None, community=None, user=None):
        """ Look up the frequency of all tags matching the given set.

        o If 'tags' is None, return frequencies for all known tags.

        o If 'community' is not None, restrict counts to items within
          the given community.

        o If 'user' is not None, restrict counts to items tagged by the
          given user.

        o Return tuples in the form of ('tag', frequency)
        """

    def update(item, user, tags):
        """ Update the tagging engine for an item and user and its tags.

        o 'item' is an integer (a 'docid')

        o 'user' is string (the login name of the user)

        o 'tags' is an iterable of tag names (unicode strings).

        o Remove existing tags which are not in 'tags'.
        """

    def delete(item=None, user=None, tag=None):
        """ Remove all tag entries matching the given criteria

        o If 'item' is None, do not filter on items.

        o If 'user' is None, do not filter on users.

        o If 'tag' is None, do not filter on users.

        o Raise ValueError if all three criteria are None.

        o Return the number of tags deleted.
        """

    def rename(old, new):
        """ Rename tags from 'old' to 'new'.

        o Joins the tags if tags with the new name already exist.

        o Return the number of tags renamed.
        """

    def normalize(normalizer):
        """Normalize tagnames with the given normalizer function

        o 'normalizer' must be either a callable, taking a single
          unicode argument and returning unicode.  It defaults to
          'unicode.lower'.

        o Return the number of tags normalized.
        """

class ITaggingStatistics(Interface):
    """ Provide statistical information about an ITaggingEngine.
    """
    def __len__():
        """ Return a count of all tags in the store.
        """

    tagCount = Int(
            title = u'Tags',
            description = u'The number of tags in the tagging engine',
            required = True,
            )

    itemCount = Int(
            title = u'Items',
            description = u'The number of items in the tagging engine',
            required = True,
            )

    userCount = Int(
            title = u'Users',
            description = u'The number of users in the tagging engine',
            required = True,
            )


class ITagCommunityFinder(Interface):
    """ Adapter interface for finding the community for an item.
    """
    def __call__(docid):
        """ Return the community name for item, or None.
        """
