GRC Envelop

GRC Envelop is a web-based work flow and document storage tool specific for the audit environment. Mainly used for internal and external audits focused on financial, IT, HR and sales processes within large corporations.

This tools falls under a broad category of services called GRC which stands for goverance, risk and compliance. 

Envelop is modelled using a basic workflow that starts from a business process. 

Process is the highest level of audit related info in the firm. There can be numerous processes. Each process has a title, description and workpapers that can be attached to it. Each process can have many objectives.

Objective may be associated with many processes (many to many relation). When creating an objective, it has to be associated to atleast one process. Each objective has a title, description and workpapers that can be attached to it. Each objective can have many risks.

Risk may be associated with many objectives (many to many relation). When creating a risk, it has to be associated to atleast one objective. Each risk has a title, description and workpapers that can be attached to it. Each risk can have many controls.

Control may be associated with many risks (many to many relation). When creating a control, it has to be associated to atleast one risk. Each control has a title, description and workpapers that can be attached to it. Each control can have many tests.

Test may be associated with many controls (many to many relation). When creating a test, it has to be associated to atleast one control. Each test has a title, description and workpapers that can be attached to it. Each test can have many findings.


The tool has following major parts:
Audit list: this part contains the list of audits that are active in the tool. Each audit has a title, decription, start and end dates, status (draft or active). Different audits could be at different stages of completion and be accessed by different users. Attaching large files as workpapers is possible through the file upload. Once the audit is complete, the generation of an audit report is possible through the Generate Report.
Users: only users explicitly allowed can used this tool or parts of this tool. There is a role based access to the entire tool.
Repository: this contains all the processes and related auditing aspects for the organisation. Consider this the library or template from which audits are created. The Repository is not available in the free community version.
Admin: the basic administration of the tool.

How to install Envelop

On a local machine (Debian 8), install the following :
* apache2
* python3
* mod_wsgi (libapache2-mod-wsgi-py3)
* python3-pip
* postgres DB (if you are not using SQLite3)
* python3-psycopg2 (not required for SQLite3)
* create the DB and user (remember to grant permissions)
	sudo su - postgres
	psql
	CREATE DATABASE envelop;
	CREATE USER myprojectuser WITH PASSWORD 'password';
	ALTER ROLE myprojectuser SET client_encoding TO 'utf8';
	ALTER ROLE myprojectuser SET default_transaction_isolation TO 'read committed';
	ALTER ROLE myprojectuser SET timezone TO 'UTC';
	GRANT ALL PRIVILEGES ON DATABASE envelop TO myprojectuser;
	\q
* Unzip or Untar the file you downloaded from http://www.grcenvelop.com/download to a folder of your choice.

Now using pip3 install the following (you may also create a virtual environment and install these in there)
* pip3 install Django

Settings and permissions
* give read execute /path/to/folder/envelop/wsgi.py (make sure the webserver user can read and execute)
* configure /path/to/folder/envelop/settings.py (No need to change if you are using SQLite3)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'envelop',
        'USER': 'myprojectuser',
        'PASSWORD': 'password',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

* go to /path/to/folder
* create directory called "media" (make sure that the webserver can read and write to this folder)
* python3 manage.py makemigrations
* python3 manage.py migrate
* python3 manage.py createsuperuser
* python3 manage.py runserver 0.0.0.0:8000
* login using the superuser credentials
* if you'd like to load some initial data then run python3 manage.py loaddata audits/fixtures/initial_data.json

Keep in mind that this installation is not to be used in production! 

Contact hello@grcenvelop.com for getting support.
