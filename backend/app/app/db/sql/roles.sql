create role admin noinherit createrole;
create role user noinherit;

create policy user_all on "user" using (role = 'admin')
