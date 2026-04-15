# myapi2

I created the database table in Supabase

Then I opened the Supabase SQL Editor and run:

create table "f1_drivers" (
  "driver_name" text primary key,
  "first_name" text not null,
  "last_name" text not null,
  "country_of_origin" text not null,
  "birthdate" date not null
);

insert into "f1_drivers"
  ("driver_name", "first_name", "last_name", "country_of_origin", "birthdate")
values
  ('Lewis Hamilton', 'Lewis', 'Hamilton', 'United Kingdom', '1985-01-07'),
  ('Max Verstappen', 'Max', 'Verstappen', 'Netherlands', '1997-09-30'),
  ('Charles Leclerc', 'Charles', 'Leclerc', 'Monaco', '1997-10-16'),
  ('Lando Norris', 'Lando', 'Norris', 'United Kingdom', '1999-11-13'),
  ('Kimi Antonelli', 'Kimi', 'Antonelli', 'Italy', '2006-08-25');

To deploy Install: pip install -r requirements.txt

command: uvicorn myserver:app --host 0.0.0.0 --port 8001 --reload

environment variables: SUPABASE_URL SUPABASE_KEY
