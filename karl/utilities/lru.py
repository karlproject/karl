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

import threading

_marker = object()

class LRUCache(object):
    """ Implements a pseudo-LRU algorithm (CLOCK) """
    lock = threading.Lock()
    def __init__(self, size):
        self.size = size
        self.maxpos = size - 1
        self.clear()

    def clear(self):
        size = self.size
        if size < 1:
            raise ValueError('size must be >1')
        self.clock = []
        for i in xrange(0, size):
            self.clock.append({'key':_marker, 'ref':False})
        self.hand = 0
        self.data = {}

    def get(self, key, default=None):
        try:
            datum = self.data[key]
        except KeyError:
            return default
        pos, val = datum
        self.clock[pos]['ref'] = True
        hand = pos + 1
        if hand > self.maxpos:
            hand = 0
        self.hand = hand
        return val

    def __setitem__(self, key, val, _marker=_marker):
        hand = self.hand
        maxpos = self.maxpos
        clock = self.clock
        data = self.data
        lock = self.lock

        end = hand - 1
        if end < 0:
            end = maxpos

        while 1:
            current = clock[hand]
            ref = current['ref']
            if ref is True:
                current['ref'] = False
                hand = hand + 1
                if hand > maxpos:
                    hand = 0
            elif ref is False or hand == end:
                lock.acquire()
                try:
                    oldkey = current['key']
                    if oldkey is not _marker:
                        try:
                            del data[oldkey]
                        except KeyError:
                            pass
                    current['key'] = key
                    current['ref'] = True
                    data[key] = (hand, val)
                    hand += 1
                    if hand > maxpos:
                        hand = 0
                    self.hand = hand
                finally:
                    lock.release()
                break
        
