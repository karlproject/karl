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

from zope.interface import Attribute
from zope.interface import Interface

class IContentSource(Interface):
    """
    Instances of IContentSource expose a datasource from which content can be
    pulled into Karl.
    """
    id = Attribute("id",
        """
        A globally unique identifier which identifies the data source.
        """
        )

    path = Attribute("path",
        """
        Path string to a container object which will receive the imported
        content items. The path is relative to a container object specified as
        part of the import/sync process, which is not known to the content
        source. Path may be an empty string, indicating the root container for
        sync."""
        )

    last_modified = Attribute("last_modified",
        """
        An instance of datetime.datetime which the last time any content in
        this source was modified. If the most recent sync is more recent than
        this timestamp, no syncronization will be performed."
        """
        )

    items = Attribute("items",
        """
        An iterable object which iterates over individual IcontentItem instances
        in the content source.
        """
        )

    incremental = Attribute("incremental",
        """
        A boolean indicating whether the the items are the full list of content
        items for this resource or partial update containing only new or
        recently updated items.  If incremental is False, then any missing
        content items will be assumed to have been deleted and will be deleted
        in Karl.
        """
        )

    deleted_items = Attribute("deleted_items",
        """
        This is an iterable containing ids of recently deleted items.  These
        items will also be deleted in Karl.  This is primarily useful in the
        context of an incremental update, where deletion isn't implied by
        ommission.
        """
        )

class IContentItem(Interface):
    """
    Instances of IContentEntry represent individual content items contained
    by an IContentSource.
    """
    id = Attribute("id",
        """
        A globally unique identifier which identifies the content item. Do not
        confuse this with the item's name.
        """
        )

    path = Attribute("path",
        """
        Path string to container object for this item.  It is considered to be
        relative to the path specified for the containing instance of
        IContentSource.
        """
        )

    name = Attribute("name",
        """
        The name of the object to either be created or updated inside the
        container specified by the content source.
        """
        )

    type = Attribute("type",
        """
        The content type, generally an interface class, for this item. Will
        be used by repoze.lemonade to look up a factory to create this item.
        """
        )

    attributes = Attribute("attributes",
        """
        Dictionary of name:value pairs of the attributes to be set on this
        content item. Values should be already converted to proper Python
        values, as opposed to being a string representation.
        """
        )

    factory_signature = Attribute("factory_signature",
        """
        Comma seperated list of attributes to pass as arguments to
        repoze.lemonade factory for this item's content type. Positional
        arguments are specified first and are just the attribute name. Keyword
        arguments are the argument key followed by an '=' character, followed
        by the attribute name to set. Ex: 'foo, bar, content=content'
        """
        )

    workflow_state = Attribute("workflow_state",
        """
        If a workflow is defined for this item, workflow state will be set to
        this state.
        """
        )

    created = Attribute("created",
        """
        Instance of datetime.datetime indicating time this content item was
        created.
        """
        )

    created_by = Attribute("created_by",
        """
        User name of user who created this content item. User must exist in
        Karl.
        """
        )

    last_modified = Attribute("last_modified",
        """
        An instance of datetime.datetime which represents the time of the
        last modification to this content item. Can be used to determine
        whether the content item in Karl needs to be updated.
        """
        )

    last_modified_by = Attribute("last_modified_by",
        """User name of user who last modified this content item. User must
        exist in Karl.
        """
        )