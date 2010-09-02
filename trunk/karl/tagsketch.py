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

import itertools
import operator
import pprint

zerogetter = operator.itemgetter(0)

tag_user_item = {}
tag_item_user = {}
user_item_tag = {}

two_dimensional = {
    'item':('tag', 'user', tag_user_item),
    'user':('tag', 'item', tag_item_user),
    'tag': ('user', 'item', user_item_tag),
    }


user_tag = {}
tag_user = {}
user_item = {}
item_user = {}
item_tag = {}
tag_item = {}

# missing: user_tag, item_tag

one_dimensional = {
    'user':{'tag':tag_user, 'item':item_user},
    'tag': {'item':item_tag, 'user':user_tag},
    'item':{'user':user_item, 'tag':tag_item},
    }

class ref(object):
    def __init__(self):
        self.set = set()
        self.counts = {}
        
    def add(self, item):
        self.set.add(item)
        if self.counts.get(item) is None:
            self.counts[item] = 0
        count = self.counts[item] = self.counts[item] + 1
        return count

    def decref(self, item):
        if not (item in self.set):
            raise KeyError(item)
        self.counts[item] = self.counts[item] - 1
        count = self.counts[item]
        if count <= 0:
            del self.counts[item]
            self.set.remove(item)
            return False
        return True

    def remove(self, item):
        try:
            del self.counts[item]
        except KeyError:
            pass
        self.set.remove(item)

    def count(self, item):
        return self.counts[item]

    def __getattr__(self, name):
        return getattr(self.set, name)

    def __iter__(self):
        return iter(self.set)

    def __repr__(self):
        return '%s->%s' % (repr(self.set), repr(self.counts))

def add(tag, item, user):
    tag_user_item.setdefault(tag, {}).setdefault(user, set()).add(item)
    tag_item_user.setdefault(tag, {}).setdefault(item, set()).add(user)
    user_item_tag.setdefault(user, {}).setdefault(item, set()).add(tag)
    user_tag.setdefault(user, ref()).add(tag)
    tag_user.setdefault(tag, ref()).add(user)
    user_item.setdefault(user, ref()).add(item)
    item_user.setdefault(item, ref()).add(user)
    item_tag.setdefault(item, ref()).add(tag)
    tag_item.setdefault(tag, ref()).add(item)

def remove(tag, item, user):
    Q = {'tag':tag, 'item':item, 'user':user}
    for dimension in ('tag', 'user', 'item'):
        otherdim1, otherdim2, index = two_dimensional[dimension]
        # if dimension=='tag', otherdim1='user', otherdim2='item'
        other1, other2, dimval = Q[otherdim1], Q[otherdim2], Q[dimension]
        tmp1 = index.get(other1)
        if tmp1:
            if other2 in tmp1:
                tmp2 = tmp1[other2]
                if tmp2:
                    if dimval in tmp2:
                        tmp2.remove(dimval)
                    if not tmp2:
                        del tmp1[other2]
                        tmp3 = one_dimensional[otherdim2][otherdim1][other1]
                        print 'considering %s_%s' % (otherdim1, otherdim2)
                        if other2 in tmp3:
                            tmp3.decref(other2)
                        tmp4 = one_dimensional[otherdim2][dimension][dimval]
                        print 'considering %s_%s' % (dimension, otherdim2)
                        if other2 in tmp4:
                            tmp4.decref(other2)
            if not tmp1:
                del index[other1]
                tmp5 = one_dimensional[dimension][otherdim1][other1]
                print 'considering %s_%s' % (otherdim1, dimension)
                if dimval in tmp5:
                    tmp5.decref(dimval)
                tmp6 = one_dimensional[dimension][otherdim2][other2]
                print 'considering %s_%s' % (otherdim2, dimension)
                if dimval in tmp6:
                    tmp6.decref(dimval)
        
    users = tag_user_item.get(tag, {})
    if users:
        if user in users:
            items = users[user]
            if items:
                if item in items:
                    items.remove(item)
                if not items:
                    del users[user]
                    items1 = one_dimensional['item']['user'][user]
                    if item in items1:
                        items1.decref(item)
                    items2 = one_dimensional['item']['tag'][tag]
                    if item in items2:
                        items2.decref(item)
                        
        if not users:
            del tag_user_item[tag]
            tags1 = one_dimensional['tag']['user'][user]
            if tag in tags1:
                tags1.decref(tag)
            tags2 = one_dimensional['tag']['item'][item]
            if tag in tags2:
                tags2.decref(tag)

##     items = tag_item_user.get(tag, {})
##     if items:
##         if item in items:
##             users = items[item]
##             if users:
##                 if user in users:
##                     users.remove(user)
##                 if not users:
##                     del items[item]
##                     users1 = one_dimensional['user']['item'][item]
##                     if user in users1:
##                         users1.decref(user)
##                     users2 = one_dimensional['user']['tag'][tag]
##                     if user in users2:
##                         users2.decref(user)
        
def intersect(L1, L2):
    L = set()
    for item in L1:
        if item in L2:
            L.add(item)
    return L

def product(L1, L2):
    L = set()
    for x in L1:
        for y in L2:
            L.add((x, y))
    return L

def find(path):
    while path.startswith('/'):
        path = path[1:]
    splitted = filter(None, path.split('/'))
    args = sorted(zip(splitted[0::2], splitted[1::2]))
    if not args:
        raise ValueError('not enough arguments')
    R = {}
    empty = set()
    R['item'] = empty
    R['tag'] = empty
    R['user'] = empty

    Q = {}

    for dimension, values in itertools.groupby(args, zerogetter):
        for _, value in values:
            dimq = Q.setdefault(dimension, set())
            dimq.add(value)

    looking_for = ['tag', 'item', 'user']
    have = []

    for name in Q:
        looking_for.remove(name)
        have.append(name)

    if not looking_for:
        raise ValueError('Not enough terms in query %s' % path)

    if len(Q) > 1:
        # two-dimensional query (e.g. given a user and a tag, return items)
        typ = looking_for[0]
        other1, other2, index = two_dimensional[typ]
        othervals1 = Q[other1]
        othervals2 = Q[other2]
        for item1, item2 in product(othervals1, othervals2):
            vals = index.get(item1, {}).get(item2, set())
            if R[typ] is empty:
                R[typ] = vals
            else:
                R[typ] = intersect(R[typ], vals)
    else:
        # one-dimensional query (e.g. given a user, return tags and items)
        have = have[0]
        for typ in looking_for:
            idxs = one_dimensional[typ]
            index = idxs[have]
            for name in Q[have]:
                vals = index.get(name, set())
                if R[typ] is empty:
                    R[typ] = vals
                else:
                    R[typ] = intersect(R[typ], vals)
    return R

def dump():
    maps = ('tag_item_user', 'user_item_tag', 'user_tag',
            'tag_user', 'user_item', 'item_user',
            'item_tag', 'tag_item')
    d = globals()
    for k in maps:                        
        print(k)     
        pprint.pprint(d[k])       

def assertEqual(a, b, p=None):
    if sorted(list(a)) != sorted(list(b)):
        raise AssertionError('%r != %r' % (a, b), p)

def assertQ(path, tag, item, user):
    result = find(path)
    assertEqual(tag, result['tag'], result)
    assertEqual(item, result['item'], result)
    assertEqual(user, result['user'], result)
    

if __name__ == '__main__':
    add(tag='fruit', item='orange', user='fred')
    add(tag='celprovider', item='orange', user='fred')
    add(tag='color', item='orange', user='barney')
    add(tag='color', item='blue', user='wilma')
    add(tag='song', item='blue', user='barney')
    add(tag='song', item='moon', user='wilma')

    assertQ('/tag/fruit', [], ['orange'], ['fred'])
    assertQ('/tag/celprovider', [], ['orange'], ['fred'])
    assertQ('/tag/fruit/tag/celprovider', [], ['orange'], ['fred'])
    assertQ('/tag/color', [], ['orange', 'blue'], ['barney', 'wilma'])
    assertQ('/tag/song', [], ['blue', 'moon'], ['barney', 'wilma'])
    assertQ('/user/fred', ['fruit', 'celprovider'], ['orange'], [])
    assertQ('/user/barney', ['color', 'song'], ['orange', 'blue'],[])
    assertQ('/user/wilma', ['color', 'song'], ['blue', 'moon'], [])
    assertQ('/item/orange', ['fruit', 'celprovider', 'color'], [],['fred', 'barney'])
    assertQ('/item/blue', ['color', 'song'], [], ['barney', 'wilma'])
    assertQ('/item/moon', ['song'], [], ['wilma'])
    assertQ('/user/barney/item/orange', ['color'], [], [])
    assertQ('/user/barney/tag/color', [], ['orange'], [])
    assertQ('/user/fred/item/orange', ['fruit', 'celprovider'], [], [])
    assertQ('/tag/fruit/tag/celprovider/user/fred', [], ['orange'], [])
    assertQ('/user/wilma/item/orange', [], [], [])

    remove(tag='fruit', item='orange', user='fred')
    assertQ('/tag/fruit', [], [], [])
    assertQ('/tag/celprovider', [], ['orange'], ['fred'])
    assertQ('/item/orange', ['celprovider', 'color'], [],['fred', 'barney'])
    
