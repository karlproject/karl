import json
import math
import os
import pickle
import psycopg2
import sys
import time
from ZODB.utils import u64
from pdb import pm

examples = ('allowed,karl.models.interfaces.IPosts,limit,sort_index,texts'
            '.examples.pickle')
with open(examples, 'rb') as f:
    examples = pickle.load(f)

def principals(uid):
    user = root.users.byid[uid]
    principals = list(user['groups'])
    principals.append('system.Everyone')
    principals.append('system.Authenticated')
    principals.insert(0, uid)
    return dict(query=principals, operator='or')

from karl.models.adapters import CatalogSearch
cat_searcher = CatalogSearch(root)

from karl.utilities.groupsearch import (
    IPeople, IPages, IPosts, IFiles, ICalendarEvent, ICommunity,
    WeightedQuery,
    )
def timed(func, *args):
    start = time.time()
    r = func(*args)
    return r, int((time.time() - start)*1000)

from karl.models.newtqbe import SQLCatalogSearch, qbe
sql_searcher = SQLCatalogSearch(root)
def sql_search(user, searchterm):
    common = dict(texts=searchterm, limit=5, sort_index='texts',
                  allowed=principals(user),
                  )
    results = []
    count = 0
    for iface in IPeople, IPages, IFiles, ICalendarEvent, ICommunity, IPosts:
        q = common.copy()
        q['interfaces'] = [iface]
        num, obs, _ = sql_searcher(**q)
        count += num
        results.extend([u64(ob._p_oid) for ob in obs])

    return count, results

def txt_search(user, searchterm):
    results = []
    count = 0
    for iface in IPeople, ICalendarEvent, ICommunity, IFiles, IPages, IPosts:
        q = dict(texts=searchterm,
                 can_view=principals(user)['query'],
                 interfaces=[iface]
                 )
        where = qbe.sql(root._p_jar, q, order_by='texts')
        where, rank = where.split('ORDER BY')
        rank += ' * text_coefficient '
        sql = """
        select * from newt natural join karlex
        where """ + where + " order by " + rank + " limit 5"
        #print sql
        obs = newt.db.search.search(root._p_jar, sql)
        count += len(obs)
        results.extend([u64(ob._p_oid) for ob in obs])

    return count, results

import newt.db.search

def grp_search(user, searchterm):
    where = qbe.sql(
        root._p_jar,
        dict(texts=searchterm,
             can_view=principals(user)['query'],
             ),
        order_by='texts',
        )
    where, rank = where.split('ORDER BY')
    rank += ' * text_coefficient '
    sql = ('''
    select zoid, ghost_pickle, ls_cat from (
      select
        zoid, ghost_pickle, ls_cat,
        row_number() over
           (partition by ls_cat order by '''
           + rank + ''' desc) as row
      from newt natural join karlex
      where ls_cat is not null and ''' + where + ''') _
    where row <= 5 order by ls_cat, row
    ''')

    #print sql

    results = [u64(ob._p_oid) for ob in newt.db.search.search(root._p_jar, sql)]

    return len(results), results

def gr2_search(user, searchterm):
    where = qbe.sql(
        root._p_jar,
        dict(texts=searchterm,
             can_view=principals(user)['query'],
             ),
        order_by='texts',
        )
    where, rank = where.split('ORDER BY')
    rank += ' * text_coefficient '
    sql = ('''
    select zoid, ghost_pickle, interface_name from (
      select
        zoid, ghost_pickle, interface_name,
        row_number() over
           (partition by interface_name order by '''
           + rank + ''' desc) as row
      from newt natural join karlex natural join implemented_by
      where interface_name in (
          'karl.models.interfaces.IPeople',
          'karl.models.interfaces.IPages',
          'karl.models.interfaces.IPosts',
          'karl.models.interfaces.IFiles',
          'karl.content.interfaces.ICalendarEvent',
          'karl.models.interfaces.ICommunity'
      ) and ''' + where + ''') _
    where row <= 5 order by row
    ''')

    obs = sorted(newt.db.search.search(root._p_jar, sql), key=iface_index)
    #obs = newt.db.search.search(root._p_jar, sql)
    # print sql
    # print
    # for ob in obs:
    #     print iface_index(ob), ob.docid, u64(ob._p_oid), ob
    results = [u64(ob._p_oid) for ob in obs]

    return len(results), results

def gr3_search(user, searchterm):
    where = qbe.sql(
        root._p_jar,
        dict(texts=searchterm,
             can_view=principals(user)['query'],
             ),
        order_by='texts',
        )
    where, rank = where.split('ORDER BY')
    rank += ' * text_coefficient '
    sql = ('''
    select zoid, ghost_pickle, interface_name from (
      select
        zoid, ghost_pickle, interface_name,
        row_number() over
           (partition by interface_name order by '''
           + rank + ''' desc) as row
      from newt natural join karlex natural join implemented_by
      where interfaces(class_name) && array[
          'karl.models.interfaces.IPeople',
          'karl.models.interfaces.IPages',
          'karl.models.interfaces.IPosts',
          'karl.models.interfaces.IFiles',
          'karl.content.interfaces.ICalendarEvent',
          'karl.models.interfaces.ICommunity'
      ] and ''' + where + ''') _
    where row <= 5 order by row
    ''')

    # obs = sorted(newt.db.search.search(root._p_jar, sql), key=iface_index)
    obs = newt.db.search.search(root._p_jar, sql)
    # print sql
    # print
    # for ob in obs:
    #     print iface_index(ob), ob.docid, u64(ob._p_oid), ob
    results = [u64(ob._p_oid) for ob in obs]

    return len(results), results

import karl.models.interfaces
import karl.content.interfaces
ifaces = (
      karl.models.interfaces.IPeople,
      karl.models.interfaces.IPages,
      karl.models.interfaces.IPosts,
      karl.models.interfaces.IFiles,
      karl.content.interfaces.ICalendarEvent,
      karl.models.interfaces.ICommunity
    )
ifaces = {ifaces[i]: i for i in range(len(ifaces))}
def iface_index(ob):
    for iface in ifaces:
        if iface.providedBy(ob):
                return ifaces[iface]

def cat_search(user, searchterm):
    common = dict(texts=WeightedQuery(searchterm), limit=5, sort_index='texts',
                  allowed=principals(user),
                  )
    results = []
    obs = []
    count = 0
    for iface in IPeople, IPages, IPosts, IFiles, ICalendarEvent, ICommunity:
        q = common.copy()
        q['interfaces'] = [iface]
        num, docids, resolver = cat_searcher(use_cache=False, **q)
        count += num
        obs.extend(resolver(docid) for docid in docids)
        results.extend([u64(resolver(docid)._p_oid) for docid in docids])

    # print
    # for ob in obs:
    #     print iface_index(ob), ob.docid, u64(ob._p_oid), ob

    return count, results

result_data = []

#examples = [([('allowed', 'kmainelli'), (('texts', 'all staff*'))], 0)]
examples = examples[:100]

#import pdb; pdb.set_trace()

conn = psycopg2.connect('postgresql://osf@karlstaging02.gocept.net/osf-karl')
cursor = conn.cursor()
ranks_sql = """
select class_name, zoid, rank, text_coefficient, rank*text_coefficient,
                         catrank, coefficient, catrank*coefficient, docid,
                         (rank*text_coefficient)/(catrank*coefficient)
from (
  select class_name, zoid, %s as rank, text_coefficient,
                           %s as catrank, coefficient, docid
  from karlex natural join newt
       join pgtextindex on ((state->>'docid')::int = docid)
  where zoid = any(%%s)
  )_
order by zoid;
"""

def print_ranks(oids, term):
    rank = qbe['texts'].order_by(cursor, term)
    catrank = rank.replace('(karlex.text)', '(text_vector)')
    #print ranks_sql % (rank, catrank)
    cursor.execute(ranks_sql % (rank, catrank), (oids,))
    for r in cursor:
        r = (r[0].rsplit('.', 1)[1],) + r[1:]
        print "%20s %12s %12s %5d %12s %19s %5d %12s %12s,    %g" % r

def run(f, user, texts, result, hot=True):
    name = f.__name__[:-7]
    root._p_jar.cacheMinimize()
    print name, user, texts,
    sys.stdout.flush()
    (count, cresults), t = timed(f, user, texts)
    result.update({name + '_cold_count': count, name + '_cold_t': t})
    print count, len(cresults), t,
    sys.stdout.flush()
    if hot:
        (count, results), t = timed(f, user, texts)
        result.update({name + '_hot_count': count, name + '_hot_t': t})
        print count, len(results), t
        assert results == cresults
        sys.stdout.flush()
        return results
    else:
        print
        return cresults

funcs = cat_search, txt_search, grp_search, gr2_search, gr3_search

rfuncs = funcs

def diff(r1, r2):
    r1 = {v: i for i, v in enumerate(r1)}
    r2 = {v: i for i, v in enumerate(r2)}
    d1 = [(v, i, 1) for (v, i) in r1.items() if r2.get(v) != i]
    d2 = [(v, i, 2) for (v, i) in r2.items() if r1.get(v) != i]
    return list(sorted(d1 + d2))

for example in examples:
    example, cost = example
    example = dict(example)
    user = example['allowed']
    if user not in root.users.byid:
        continue
    texts = example['texts']

    result = dict(user=user, text=texts)
    last = None
    rfuncs = rfuncs[-1:] + rfuncs[:-1] # rotate
    for func in rfuncs:
        r = run(func, user, texts, result)
        if last is not None:
            d = diff(last, r)
            if 0 and d:
                print 'diffs', d
                print_ranks(list(set(i[0] for i in d)), texts)
        last = r

    result_data.append(result)

funcs = [f.__name__[:-7] for f in funcs]

mean  = lambda l: sum(l)/len(l)
gmean = lambda l: math.exp(sum(math.log(x) for x in l)/len(l))

def perc(data, p, l):
    p = int(p*l)
    return data[p] if p < l else None

def stats(data):
    data = sorted(data)
    l = len(data)
    return (
        math.exp(sum(math.log(v) for v in data)/l),
        perc(data, .5, l),
        perc(data, .9, l),
        perc(data, .99, l),
        perc(data, .999, l),
        )

for heat in 'cold', 'hot':
    print heat
    for name in funcs:
        k = name + '_' + heat + '_t'
        print name, stats([r[k] for r in result_data])

first = funcs[0]
for i, name in enumerate(funcs[1:]):
    print name + '/' + first,
    print gmean([float(r[name + '_cold_t'])/r[first + '_cold_t']
                 for r in result_data]),
    print gmean([float(r[name + '_hot_t'])/r[first + '_hot_t']
                 for r in result_data]),
    print mean([float(r[name + '_cold_t'])/r[first + '_cold_t']
                 for r in result_data]),
    print mean([float(r[name + '_hot_t'])/r[first + '_hot_t']
                 for r in result_data]),
    print
    bad = [r for r in result_data
           if r[name + '_cold_count'] !=  r[first + '_cold_count']]
    if bad:
        print bad

funcs = ','.join(funcs)

with open('compare_search-' + funcs + '.json', 'w') as f:
    json.dump(result_data, f)
