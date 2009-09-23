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

    nodes = Attribute("nodes",
        """
        Iterable of IContentNode instances, used to traverse to particular
        containers inside Karl.
        """
        )

    content = Attribute("content",
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

    deleted_content = Attribute("deleted_content",
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

    modified = Attribute("modified",
        """
        An instance of datetime.datetime which represents the time of the
        last modification to this content item. Can be used to determine
        whether the content item in Karl needs to be updated.
        """
        )

    modified_by = Attribute("last_modified_by",
        """
        User name of user who last modified this content item. User must
        exist in Karl.
        """
        )

    children = Attribute("children",
        """
        Instances of IContentItem contained by this item in the containment
        hierarchy.
        """
        )

    deleted_children = Attribute("deleted_children",
        """
        List of ids of children recently deleted from this item.  This is only
        necessary if doing an incremental update.  Otherwise, deleted children
        can be communicated implicitly via omission from ``children``.
        """
        )

class IContentNode(Interface):
    """
    A node is like an item excpet it is merely traversed.  No update or create
    is performed.  It must correspond to an actually existing container object
    in Karl and is used to indicate that any children of this node should be
    imported into that container object.
    """

    name = Attribute("name",
        """
        The object.__name__ of the node to be traversed.
        """
        )

    nodes = Attribute("nodes",
        """
        Any child nodes of this node.
        """
        )

    content = Attribute("content",
        """
        Instances of IContentItem contained by this node.
        """
        )

    deleted_content = Attribute("deleted_content",
        """
        List of ids of children recently deleted from this node.  This is only
        necessary if doing an incremental update.  Otherwise, deleted children
        can be communicated implicitly via omission from ``children``.
        """
        )

class IGenericContentFactory(Interface):
    """
    Normally, with repoze.lemonade you register content type factories as
    providers for repoze.lemonade.interfaces.IContentFactory that can have an
    arbitrary signature.  This is difficult for us to deal with if we are to be
    importing arbitrary content types--how does our tool know the signature for
    the factory?  To get around this we register factories that provide this
    interface, which provides a uniform signature for generic factory
    callables.
    """
    def __call__(attrs):
        """
        ``attrs`` is a dictionary mapping attribute names to attribute values,
        for use in constructing a content instance. The callable will return
        the object created.
        """
