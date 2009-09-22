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

from zope.interface import implements
from persistent import Persistent
from persistent.list import PersistentList

from repoze.folder import Folder
from karl.content.interfaces import IReferenceManual
from karl.content.interfaces import IReferenceSection
from karl.content.interfaces import IOrdering

class Ordering(Persistent):
    """ Handle an ordered folder """
    implements(IOrdering)

    def __init__(self):
        Persistent.__init__(self)
        self._items = PersistentList()

    def sync(self, entries):
        # Go do some cleanup.  Any items that are in the folder but
        # not in the ordering, put at end.  Any items that are in the
        # ordering but not in the folder, remove.

        for local_name in self._items:
            if local_name not in entries:
                # Item is in ordering but not in context, remove from
                # ordering.
                self._items.remove(local_name)
        for entry_name in entries:
            if entry_name not in self._items:
                # Item is in folder but not in ordering, append to
                # end.
                self._items.append(entry_name)


    def moveUp(self, name):
        # Move the item with __name__ == name up a position.  If at
        # the beginning, move to last position.

        position = self._items.index(name)
        del self._items[position]
        if position == 0:
            # Roll over to the end
            self._items.append(name)
        else:
            self._items.insert(position - 1, name)

    def moveDown(self, name):
        # Move the item with __name__ == name down a position.  If at
        # the end, move to the first position.

        position = self._items.index(name)
        list_length = len(self._items)
        del self._items[position]
        if position == (list_length - 1):
            # Roll over to the end
            self._items.insert(0, name)
        else:
            self._items.insert(position + 1, name)


    def add(self, name):
        # When a new item is added to a folder, put it at the end.

        self._items.append(name)

    def remove(self, name):
        # When an existing item is removed from folder, remove from
        # ordering.  Sure would be nice to use events to do this for
        # us.

        self._items.remove(name)

    def items(self):
        return self._items

    def previous_name(self, current_name):
        # Given a position in the list, get the next name, or None if
        # at the end of the list

        position = self._items.index(current_name)
        if position == 0:
            # We are at the end of the list, so return None
            return None
        else:
            return self._items[position - 1]

    def next_name(self, current_name):
        # Given a position in the list, get the next name, or None if
        # at the end of the list

        position = self._items.index(current_name)
        if position == (len(self._items)-1):
            # We are at the end of the list, so return None
            return None
        else:
            return self._items[position + 1]


class ReferenceSection(Folder):
    implements(IReferenceSection)
    modified_by = None

    def __init__(self, title, description, creator):
        Folder.__init__(self)
        self.title = unicode(title)
        self.description = unicode(description)
        self.creator = unicode(creator)
        self.modified_by = self.creator
        self.ordering = Ordering()

class ReferenceManual(Folder):
    implements(IReferenceManual)
    modified_by = None

    def __init__(self, title, description, creator):
        Folder.__init__(self)
        self.title = unicode(title)
        self.description = unicode(description)
        self.creator = unicode(creator)
        self.modified_by = self.creator
        self.ordering = Ordering()

