import karl.utils
import newt.db.search
from newt.qbe import QBE, match, scalar, prefix, text_array, fulltext
qbe = QBE()

# Punt, it's not used: qbe['containment']

# Comment out unused helpers:
# qbe['name'] = match('__name__')
# qbe['title'] = scalar("lower(state->>'title')")
# qbe['titlestartswith'] = scalar("upper(substring(state->>'title', 1, 1))")

#############################################################################
# interfaces

interfaces_sql = """
create or replace function interfaces(class_name_ text) returns text[] as $$
begin
  return array(select interface_name from implemented_by i
               where i.class_name = class_name_);
end
$$ language plpgsql immutable cost 99;
"""

def iface_names(ifaces):
    return [i.__module__ + '.' + i.__name__ for i in ifaces]

qbe['interfaces'] = text_array("interfaces(class_name)", convert=iface_names)

#
#############################################################################

# qbe['texts'] = fulltext("content_text(state)", 'english')

#############################################################################
# community
get_community_zoid_sql = """
create or replace function get_community_zoid(
  zoid_ bigint, class_name text, state jsonb)
  returns bigint
as $$
declare
  parent_class_name text;
  parent_state jsonb;
  parent_id bigint;
begin
  if state is null then return null; end if;
  if class_name = 'karl.models.community.Community' then
     return zoid_;
  end if;
  parent_id := (state -> '__parent__' ->> '::=>')::bigint;
  if parent_id is null then return null; end if;
  select newt.class_name, newt.state from newt where zoid = parent_id
  into parent_class_name, parent_state;

  if parent_class_name is null then
    return null;
  end if;

  return get_community_zoid(parent_id, parent_class_name, parent_state);
end
$$ language plpgsql immutable;
"""
from ZODB.utils import u64
qbe['community'] = scalar("karlex.community_zoid",
                          convert = lambda c: u64(c._p_oid))
#
#############################################################################

#############################################################################
# Path

# Needed for computing paths in sql (e.g. for office_dump).
get_path_sql = """
create or replace function get_path(state jsonb, tail text default null)
  returns text
as $$
declare
  parent_id bigint;
  name text;
begin
  if state is null then return null; end if;

  parent_id := (state -> '__parent__' ->> '::=>')::bigint;
  if parent_id is null then return tail; end if;

  name := '/' || (state ->> '__name__');
  if name is null then return tail; end if;

  tail := name || coalesce(tail, '/');

  select newt.state
  from newt
  where zoid = parent_id
  into state;

  return get_path(state, tail);
end
$$ language plpgsql immutable cost 9999;
"""
# Not searching on path at this point because needded path searches
# are for communities and the community index is much faster.
# qbe["path"] = prefix(
#     "get_path(state)", delimiter='/',
#     convert=
#     lambda p: p.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
#     )
#
#############################################################################



qbe['creation_date'] = scalar('created')
qbe['modified_date'] = scalar('modified')
# qbe['content_modified'] = scalar('content_modified')
# qbe['start_date'] = scalar('startDate')
# qbe['end_date'] = scalar('endDate')
# qbe['publication_date'] = scalar('publication_date')
# qbe['mimetype'] = match('mimetype')
qbe['creator'] = match('creator')
# qbe['modified_by'] = match('modified_by')
# qbe['email'] = scalar('email')
# qbe['tags'] = text_array("get_tags(state)")
# qbe['lastfirst'] = scalar("get_last_first(class_name, state)")
# qbe['member_name'] = fulltext("get_member_name(class_name, state)",
#                                   'simple')
# qbe['virtual'] = match("calendar_category")

#############################################################################
# can_view: unindexed security check which is sometimes faster

can_view_sql = """
create or replace function newt_can_view(state jsonb, principals text[])
  returns bool
as $$
declare
  acl jsonb;
  acli jsonb;
  parent_id bigint;
  want constant text[] := array['view', '::'];
begin
  if state is null then return false; end if;
  acl := state -> '__acl__';
  if acl is not null then
    for i in 0 .. (jsonb_array_length(acl) - 1)
    loop
      acli := acl -> i;
      if acli ->> 1 = any(principals) and acli -> 2 ?| want then
         return acli ->> 0 = 'Allow';
      end if;
    end loop;
  end if;
  parent_id := (state -> '__parent__' ->> '::=>')::bigint;
  if parent_id is null then return false; end if;
  select newt.state from newt where zoid = parent_id
  into state;
  return newt_can_view(state, principals);
end
$$ language plpgsql immutable;
"""

def can_view(cursor, query):
    return cursor.mogrify("newt_can_view(state, %s)", (query,))

qbe['can_view'] = can_view

#
#############################################################################

def ob_resolver(ob):
    # satisfy catalog api
    return ob

def dequerify(query):
    result = {}
    for name, q in query.items():
        if isinstance(q, dict) and 'query' in q:
            assert q.pop('operator', 'or') == 'or'
            assert len(q) == 1
            q = q['query']
        result[name] = q
    return result

class SQLCatalogSearch(object):

    def __init__(self, context, request=None):
        self.context = context

    def __call__(self, sort_index=None, reverse=False,
                 offset=None, limit=None, want_count=True,
                 **kw):
        sql = self.sql(sort_index, reverse, offset, limit, want_count, **kw)

        conn = self.context._p_jar
        if limit is not None:
            if want_count:
                count, obs = newt.db.search.search_batch(
                    conn, sql, offset or 0, limit)
                return count, obs, ob_resolver

            sql += ' limit %d' % limit

        obs = newt.db.search.search(conn, sql)
        return len(obs), obs, ob_resolver

    def sql(self, sort_index=None, reverse=False,
            offset=None, limit=None, want_count=True,
            **kw):
        if sort_index is not None:
            order_by = [(sort_index, reverse)]
        else:
            order_by = ()

        sql = qbe.sql(self.context._p_jar, dequerify(kw), order_by=order_by)
        if 'community' not in kw:
            sql = "state ? '__parent__' AND state ? '__name__' AND \n" + sql

        if 'karlex.' in sql:
            sql = 'select * from newt natural join karlex\nwhere ' + sql
        else:
            sql = 'select * from newt\nwhere ' + sql


        if limit is not None and not want_count:
            sql += ' limit %d' % limit

        return sql
