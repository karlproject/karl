create or replace function get_ls_cat(class_name_ text) returns int
as $$
declare
  ifaces text[] := array['karl.models.interfaces.IPeople',
                         'karl.models.interfaces.IPages',
                         'karl.models.interfaces.IPosts',
                         'karl.models.interfaces.IFiles',
                         'karl.content.interfaces.ICalendarEvent',
                         'karl.models.interfaces.ICommunity'];
  r int;
begin
  select pos from (
    select array_position(ifaces, interface_name) as pos
    from implemented_by
    where class_name = class_name_) _
  where pos is not null
  into r;
  return r;
end;
$$ language plpgsql stable;

alter table karlex add ls_cat integer;

update karlex set ls_cat = get_ls_cat(class_name)
from newt where newt.zoid = karlex.zoid;
