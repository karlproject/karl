
create or replace function get_tags(state_ jsonb) returns text[]
as $$
begin
  return array(select distinct state->>'name'
               from newt
               where class_name = 'karl.tagging.Tag' and
                     state @> ('{"item": ' || (state_->>'docid') || '}')::jsonb
               );
end
$$ language plpgsql stable;

create or replace function content_text(class_name text, state jsonb)
  returns tsvector as $$
declare
  -- A text;
  B text;
  C text;
  D text;
  hoid bigint;
begin
  if state is null then return null; end if;

  if class_name in ('karl.content.models.calendar.CalendarLayer',
                    'karl.content.models.calendar.CalendarCategory') then
     return null;
  end if;

  if class_name not in (
      select implemented_by.class_name
      from implemented_by
      where interface_name = 'repoze.lemonade.interfaces.IContent') then
    return null;
  end if;

  -- search_keywords was a misfeature and only applied to 169 content items
  -- A = coalesce(
  --       array_to_string(
  --         array(select *
  --               from jsonb_array_elements_text(state->'search_keywords')),
  --         ' '),
  --       '')
  B = array_to_string(get_tags(state), ' ');
  C := coalesce(state->>'title', '');

  if class_name = 'karl.models.profile.Profile' then
    C := coalesce(state ->> 'firstname', '') || ' ' ||
         coalesce(state ->> 'lastname', '');
    if state->> 'security_state' = 'inactive' then
      C := C  || ' (Inactive)';
    end if;
    D :=
      coalesce(state ->> '__name__', '')
      || ' ' || coalesce(state ->> 'firstname', '')
      || ' ' || coalesce(state ->> 'lastname', '')
      || ' ' || coalesce(state ->> 'email', '')
      || ' ' || coalesce(state ->> 'phone', '')
      || ' ' || coalesce(state ->> 'extension', '')
      || ' ' || coalesce(state ->> 'department', '')
      || ' ' || coalesce(state ->> 'position', '')
      || ' ' || coalesce(state ->> 'organization', '')
      || ' ' || coalesce(state ->> 'location', '')
      || ' ' || coalesce(state ->> 'country', '')
      || ' ' || coalesce(state ->> 'website', '')
      || ' ' || coalesce(state ->> 'languages', '')
      || ' ' || coalesce(state ->> 'office', '')
      || ' ' || coalesce(state ->> 'room_no', '')
      || ' ' || coalesce(state ->> 'biography', '');
  elseif class_name = 'karl.content.models.files.CommunityFile' then
    hoid := (state -> '_extracted_data' ->> '::=>')::bigint;
    if hoid is not null then
      select newt.class_name, newt.state
      from newt where zoid = hoid
      into class_name, state;
      if class_name != 'karl.content.models.adapters._CachedData' then
        raise 'bad data in CommunityFile % %', hoid, class_name;
      end if;
      D := coalesce(state ->> 'text', '');
    else
      D := '';
    end if;
  elseif class_name in (
      'karl.content.models.blog.BlogEntry',
      'karl.content.models.calendar.CalendarEvent',
      'karl.content.models.wiki.WikiPage',
      'karl.content.models.commenting.Comment') then
    D := coalesce(state->>'text', '');
  elseif class_name in (
      'karl.content.models.references.ReferenceManual',
      'karl.content.models.references.ReferenceSection') then
    D := coalesce(state->>'description', '');
  else
    D := coalesce(state->>'text', '');
    C := C || ' ' || coalesce(state->>'description', '');
  end if;

  if length(D) > 70000 then
    D := regexp_replace(substring(D from 0 for 70000), '\w+$', '');
  end if;

  return --setweight(to_tsvector('english', A), 'A') ||
         setweight(to_tsvector('english', B), 'B') ||
         setweight(to_tsvector('english', C), 'C') ||
         setweight(to_tsvector('english', D), 'D');
end
$$ language plpgsql stable;

create or replace function content_text(zoid_ bigint) returns tsvector
as $$
declare
  res tsvector;
begin
  select content_text(class_name, state) from newt where zoid = zoid_ into res;
  return res;
end
$$ language plpgsql stable;

create or replace function content_text_coefficient(state jsonb) returns real
as $$
declare
  coefficient real;
begin
  if state is null or jsonb_typeof(state) != 'object' then
    return null;
  end if;
  coefficient := 32 ^ coalesce(state->>'search_weight', '0')::real;
  if coalesce(state->>'is_created_by_staff', '') = 'true' then
    coefficient := coefficient * 25;
  end if;
  return coefficient;
end
$$ language plpgsql stable;

create or replace function content_text_coefficient(zoid_ bigint) returns real
as $$
declare
  res real;
begin
  select content_text_coefficient(state) from newt where zoid = zoid_ into res;
  return res;
end
$$ language plpgsql stable;
