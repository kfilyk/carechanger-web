# The CareChanger Web Platform

A Heroku web app running Django with a PostgreSQL backend. The CareChanger platform connects a live-feed of medical data from wifi-connected microcontrollers to a private caregroup database. This data powers patient status graphs, as well as an event-driven alert system.

This web framework was designed and built by Ross, Kelvin, and Misha of the University of Victoria Biomedical Club.

# LOGIN

username: testuser
email: kelvinfilyk@gmail.com
pass: carechanger

# LOCAL SETUP

1. python manage.py createsuperuser - create admin for testing/access purposes
2. python manage.py migrate - build database for storing admin/general gathered data
3. python manage.py runserver - run site locally
4. python manage.py makemigrations - Whenever updating database schema, run 'makemigrations' to instantiate changes. Then rerun step 2 to commit them. 
5. .mode csv / .import Data.csv sensors_data --skip 1 - Use this to load example sensor data into sensors_data table. '--skip 1' avoids inputting the header row

# DATABASE
Extra help: https://docs.djangoproject.com/en/3.2/intro/tutorial02/
Database models can be found in sensors/models.py. To browse database, use:

sqlite3 db.sqlite3

.headers ON - Makes table column headers visible
.tables - list tables
.databases - list databases
.schema <tablename> - get the schema of a table
select * from <tablename>;
ctrl + D -  exit sqlite3

# FAQ

- 'models.py' contains database objects (patient, device, caregroup, etc.)
- 'views.py' contains functions that are run as soon as a given page is loaded (dashboard.html runs the 'dashboard' function). These mappings are listed in 'urls.py'.
- 'forms.py' contain form middleware for creating new instances of classes in 'models.py' and saving them to the database.
- 'sensors.js' mostly contains functionality used by 'dashboard.html' to pull and render patient statistics from the database.