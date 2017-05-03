"""
This file contains the local settings and overrides the default ones.
"""
import os

# Set the root_path to the root of our project.
ROOT_PATH = os.path.dirname(os.path.dirname(__file__))

# Set the temporary location for the project.
TMP_PATH = os.path.join(ROOT_PATH, 'tmp')

# Create temporary folder if not exists.
if not os.path.exists(TMP_PATH):
	os.mkdir(TMP_PATH)

# Enable debug mode to get verbose output, not report any errors and dynamically use the DEBUG in your code
# for extra verbosity of logging/output.
DEBUG = True # bool(os.environ.get('PYPLANET_DEBUG', False))

# Add your pools (the controller instances per dedicated here) or leave as it is to use a single instance only.
POOLS = [
	'default',
	#'test2',
]

# Owners are logins of the server owners, the owners always get *ALL* the permissions in the system.
OWNERS = {
	'default': [
		'your-maniaplanet-login'
	]
}

# Databases configuration holds an dictionary with information of the database backend.
# Please refer to the documentation for all examples.
SQLITE = {
	'ENGINE': 'peewee.SqliteDatabase',
	'NAME': 'database.db'
}
MYSQL = {
	'ENGINE': 'peewee_async.MySQLDatabase',
	'NAME': 'pyplanet',
	'OPTIONS': {
		'host': 'localhost',
		'user': 'root',
		'password': '',
		'charset': 'utf8',
	}
}
POSTGRESQL = {
	'ENGINE': 'peewee_async.PostgresqlDatabase',
	'NAME': 'pyplanet',
	'OPTIONS': {
		'host': 'localhost',
		'user': 'pyplanet',
		'password': 'pyplanet',
		'autocommit': True,
	}
}
DATABASE_ENGINE = None
TOX_ENV = os.getenv('TOXENV', 'py36-unit-mysql')
if 'mysql' in TOX_ENV:
	DATABASE_ENGINE = MYSQL
elif 'postgresql' in TOX_ENV:
	DATABASE_ENGINE = POSTGRESQL
else:
	DATABASE_ENGINE = SQLITE
DATABASES = {
	'default': DATABASE_ENGINE
}

# Dedicated configuration holds the different dedicated servers that the instances will run on including the names of
# the instances.
DEDICATED = {
	'default': {
		'HOST': '127.0.0.1',
		'PORT': '5000',
		'USER': 'SuperAdmin',
		'PASSWORD': 'SuperAdmin',
	}
}

# The storage configuration contains the same instance mapping of the dedicated servers and is used
# to access the filesystem on the dedicated server location.
# Please refer to the documentation for more information.
STORAGE = {
	'default': {
		'DRIVER': 'pyplanet.core.storage.drivers.local.LocalDriver',
		'OPTIONS': {},
	}
}

MAP_MATCHSETTINGS = 'test.txt'

# Define any cache backends that can be used by the core and the plugins to cache data.
# CACHE = {
# 	'default': {
#
# 	}
# }
