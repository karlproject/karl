import karl.utils
import newt.db.search
from newt.qbe import QBE, match, scalar, text_array, fulltext
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
# qbe["path"] = scalar("get_path(state)")
# qbe['allowed'] = text_array('allowed_to_view(state)')
qbe['creation_date'] = scalar('created')
# qbe['modified_date'] = scalar('modified')
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
  return can_view(state, principals);
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
        if sort_index is not None:
            order_by = [(sort_index, reverse)]
        else:
            order_by = ()

        conn = self.context._p_jar
        sql = qbe.sql(conn, dequerify(kw), order_by=order_by)
        sql = "state ? '__parent__' AND state ? '__name__' AND \n" + sql

        if limit is not None:
            if want_count:
                count, obs = newt.db.search.where_batch(
                    conn, sql, offset or 0, limit)
                return count, obs, ob_resolver

            sql += ' limit %d' % limit

        obs = newt.db.search.where(conn, sql)
        return len(obs), obs, ob_resolver

    def sql(self, sort_index=None, reverse=False,
            offset=None, limit=None, want_count=True,
            **kw):
        if sort_index is not None:
            order_by = [(sort_index, reverse)]
        else:
            order_by = ()

        sql = qbe.sql(self.context._p_jar, dequerify(kw), order_by=order_by)
        sql = "state ? '__parent__' AND state ? '__name__' AND \n" + sql

        if limit is not None:
            sql += ' limit %d' % limit

        return sql
