-- 1. Create the F1 Drivers table:

create table f1_drivers (
  driver_name text primary key, -- Unique ID (e.g., 'LewisHamilton')
  first_name text not null,
  last_name text not null,
  country_of_origin text not null,
  birthdate date not null,
  inserted_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);




-- 2. Insert initial seed data:

insert into f1_drivers (driver_name, first_name, last_name, country_of_origin, birthdate)
values
  ('MaxVerstappen', 'Max', 'Verstappen', 'Netherlands', '1997-09-30'),
  ('LewisHamilton', 'Lewis', 'Hamilton', 'United Kingdom', '1985-01-07'),
  ('CharlesLeclerc', 'Charles', 'Leclerc', 'Monaco', '1997-10-16'),
  ('LandoNorris', 'Lando', 'Norris', 'United Kingdom', '1999-11-13'),
  ('FernandoAlonso', 'Fernando', 'Alonso', 'Spain', '1981-07-29');




  To deploy install: pip install -r requirements.txt


  To run the server command: uvicorn myserverauth:app --host 0.0.0.0 --port 8000 --reload


  environment variables: SUPABASE_URL   SUPABASE_KEY   MY_API_KEY

  
