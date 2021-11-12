# The CareChanger Web Platform

A Heroku web app running Django with a PostgreSQL backend. The CareChanger platform connects a live-feed of medical data from wifi-connected microcontrollers to a private caregroup database. This data powers patient status graphs, as well as an event-driven alert system.

This web framework was designed and built by Ross, Kelvin, and Misha of the University of Victoria Biomedical Club.

# PASSWORDS

- SUPERUSER: kfilyk / kelvinfilyk@gmail.com / carechanger
- CAREGROUP: cg1 / carechanger
- POSTGRES (LOCAL): kfilyk / pass

# LOCAL SETUP

1. python manage.py createsuperuser - create admin for testing/access purposes
2. python manage.py makemigrations/migrate - build database for storing admin/general gathered data, then commit changes
3. python manage.py runserver - run site locally
4. .mode csv / .import Data.csv sensors_data --skip 1 - Use this to load example sensor data into sensors_data table. '--skip 1' avoids inputting the header row

# REMOTE SETUP
1. setup settings.py with proper credentials for heroku backend database: https://dev.to/prisma/how-to-setup-a-free-postgresql-database-on-heroku-1dc1
2. heroku run python manage.py makemigrations/migrate --app carechanger
3. heroku run:detached python manage.py createsuperuser --app carechanger - create a superuser for the project
4. heroku pg:psql postgresql-curved-14194 --app carechanger - access remote project instance of postgres 
5. \copy sensors_data from '/Users/kelvinfilyk/Desktop/Projects/carechanger-web/data.csv' delimiter ',' csv header; - remote copy data from csv to table


# DATABASE

- SQLITE3 (local, small db)
Extra help: https://docs.djangoproject.com/en/3.2/intro/tutorial02/
Database models can be found in sensors/models.py. To browse database, use:
sqlite3 db.sqlite3

.headers ON - Makes table column headers visible
.tables - list tables
.databases - list databases
.schema <tablename> - get the schema of a table
select * from <tablename>;
ctrl + D -  exit sqlite3


- POSTGRES (production quality/scale db)
https://medium.com/@viviennediegoencarnacion/getting-started-with-postgresql-on-mac-e6a5f48ee399
https://chartio.com/resources/tutorials/how-to-list-databases-and-tables-in-postgresql-using-psql/
https://www.enterprisedb.com/postgres-tutorials/how-use-postgresql-django
local brew services start/stop postgresql - starts/stops the local database instance
psql postgres - enter postgres and perform queries
\q - quit postgres terminal
Local user account: 'kfilyk', 'pass'
psql postgres -U kfilyk
\l - list databases
create database carechanger - creates database
python manage.py migrate - process database schema code
python manage.py makemigrations - push database schema to database 'carechanger'
python manage.py createsuperuser (setup using credentials above)
\c carechanger - connect to db
copy sensors_data from '/Users/kelvinfilyk/Desktop/Projects/carechanger-web/Data.csv' delimiter ',' csv header; - must be a superuser

# FAQ

- 'models.py' contains database objects (patient, device, caregroup, etc.)
- 'views.py' contains functions that are run as soon as a given page is loaded (dashboard.html runs the 'dashboard' function). These mappings are listed in 'urls.py'.
- 'forms.py' contain form middleware for creating new instances of classes in 'models.py' and saving them to the database.
- 'sensors.js' mostly contains functionality used by 'dashboard.html' to pull and render patient statistics from the database.

# TODO

- Notification when a caregroup is attempted to be created with same name as other caregroup
- Notification when a signup user/pass combination is not good enough/hacked/invalid
- 
