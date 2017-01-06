create or replace function can_view(
  state jsonb,
  principals text[])
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
  parent_id := (state -> '__parent__' -> 'id' ->> 0)::bigint;
  if parent_id is null then return false; end if;
  select object_json.state from object_json where zoid = parent_id
  into state;
  return can_view(state, principals);
end
$$ language plpgsql immutable;
