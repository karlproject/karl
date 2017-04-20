
-----------------------------------------------------------------------------
-- interfaces

create or replace function interfaces(class_name_) return text[]
as $$
begin
  return array(select interface_name
               from implemented_by i
               where i.class_name = class_name_);
end
$$ language plpgsql immutable;

-----------------------------------------------------------------------------
-- texts

create or replace function content_text(class_name varchar, state jsonb)
  returns tsvector as $$
declare
  text varchar;
  textv tsvector;
  hoid bigint;
begin
  if state is null then return null; end if;
  if class_name = 'karl.models.profile.Profile' then
    text :=
      coalesce(state #>> '{"__name__"}', '')
      || ' ' || coalesce(state #>> '{"firstname"}', '')
      || ' ' || coalesce(state #>> '{"lastname"}', '')
      || ' ' || coalesce(state #>> '{"email"}', '')
      || ' ' || coalesce(state #>> '{"phone"}', '')
      || ' ' || coalesce(state #>> '{"extension"}', '')
      || ' ' || coalesce(state #>> '{"department"}', '')
      || ' ' || coalesce(state #>> '{"position"}', '')
      || ' ' || coalesce(state #>> '{"organization"}', '')
      || ' ' || coalesce(state #>> '{"location"}', '')
      || ' ' || coalesce(state #>> '{"country"}', '')
      || ' ' || coalesce(state #>> '{"website"}', '')
      || ' ' || coalesce(state #>> '{"languages"}', '')
      || ' ' || coalesce(state #>> '{"office"}', '')
      || ' ' || coalesce(state #>> '{"room_no"}', '')
      || ' ' || coalesce(state #>> '{"biography"}', '');
  elseif class_name = 'karl.content.models.files.CommunityFile' then
    hoid := (state #>> '{"_extracted_data", "id", 0}')::bigint;
    if hoid is not null then
      select object_json.class_name, object_json.state
      from object_json where zoid = hoid
      into class_name, state;
      if class_name != 'karl.content.models.adapters._CachedData' then
        raise 'bad data in CommunityFile % %', hoid, class_name;
      end if;
      text := coalesce(state #>> '{"text"}', '');
    else
      text := '';
    end if;
  elseif class_name = 'karl.content.models.adapters._CachedData' then
    return null;
  else
    text := coalesce(state #>> '{"text"}', '');
  end if;

  textv := to_tsvector(text);

  if state ? 'title' then
    textv := textv
      || setweight(to_tsvector(state #>> '{"title"}'), 'A')
      || setweight(to_tsvector(coalesce(state #>> '{"description"}', '')), 'B');
  else
    textv := textv
      || setweight(to_tsvector(coalesce(state #>> '{"description"}', '')), 'A');
  end if;

  return textv;
end
$$ language plpgsql immutable;

-----------------------------------------------------------------------------
-- path

create or replace function get_path(
  state jsonb,
  tail text default null
  ) returns text
as $$
declare
  parent_id bigint;
  name text;
begin
  if state is null then return null; end if;

  parent_id := (state -> '__parent__' -> 'id' ->> 0)::bigint;
  if parent_id is null then return tail; end if;

  name := '/' || (state ->> '__name__');
  if name is null then return tail; end if;

  tail := name || coalesce(tail, '/');

  select object_json.state
  from object_json
  where zoid = parent_id
  into state;

  return get_path(state, tail);
end
$$ language plpgsql immutable;

-----------------------------------------------------------------------------
-- allowed

create or replace function get_allowed_to_view(
  state jsonb,
  allowed text[],
  denied text[])
  returns text[]
as $$
declare
  p text[];
  acl jsonb;
  acli jsonb;
  parent_id bigint;
  want constant text[] := array['view', '::'];
  Everyone constant text[] := array['system.Everyone'];
  Allow constant text := 'Allow';
begin
  if state is null then return allowed; end if;
  acl := state -> '__acl__';
  if acl is not null then
    for i in 0 .. (jsonb_array_length(acl) - 1)
    loop
      acli := acl -> i;
      if acli -> 2 ?| want then
        p := array[acli ->> 1];
        if p = Everyone and acli ->> 0 != Allow then
          return allowed; -- Deny Everyone is a barrier
        end if;
        if not (allowed @> p or denied @> p) then
          if acli ->> 0 = Allow then
            allowed := allowed || p;
          else
            denied := denied || p;
          end if;
        end if;
          
      end if;
    end loop;
  end if;
  parent_id := (state -> '__parent__' -> 'id' ->> 0)::bigint;
  if parent_id is null then return allowed; end if;
  select object_json.state from object_json where zoid = parent_id
  into state;
  return get_allowed_to_view(state, allowed, denied);
end
$$ language plpgsql immutable;

create or replace function allowed_to_view(state jsonb) returns text[]
as $$
begin
  return get_allowed_to_view(state, array[]::text[], array[]::text[]);
end
$$ language plpgsql immutable cost 9999;

-----------------------------------------------------------------------------
-- tags

create or replace function get_tags(state_ jsonb) returns text[]
as $$
begin
  return array(select state->>'name'
               from newt
               where class_name = 'karl.tagging.Tag' and
                     state @> ('{"item": ' || state_->>'docid' || '}')::jsonb
               );
end
$$ language plpgsql immutable cost 9999;

-----------------------------------------------------------------------------
-- get_lastfirst

create or replace function get_tags(cls, text, state jsonb) returns text
as $$
begin
  if cls = karl.models.profile.Profile then
    return state->>lastname || ", " || state->firstname;
  end if;
end
$$ language plpgsql immutable cost 9999;

-----------------------------------------------------------------------------
-- get_member_name

create or replace function get_member_name(cls, text, state jsonb)
  returns tsvector
as $$
begin
  if cls = karl.models.profile.Profile then
    return to_tsvector('english', coalesce(state->>lastname, '')
                                  || " " ||
                                  coalesce(state->firstname, ''));
  end if;
end
$$ language plpgsql immutable cost 9999;
