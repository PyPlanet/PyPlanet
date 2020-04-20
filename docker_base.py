"""
This file contains the basic settings and overrides the default ones that are defined in the core.
Documentation: http://pypla.net/

If you want to use other configuration methods like YAML or JSON files, take a look at http://pypla.net/ and head to the
configuration pages.
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
DEBUG = bool(os.environ.get('PYPLANET_DEBUG', False))

# Add your pools (the controller instances per dedicated here) or leave as it is to use a single instance only.
POOLS = [
	'default'
]

# Owners are logins of the server owners, the owners always get *ALL* the permissions in the system.
OWNERS = {
	'default': [
		os.getenv('MANIAPLANET_OWNER_LOGIN', '')
	]
}

# Allow self-upgrading the installation. Disable on shared servers with one installation (hosting environment)!
SELF_UPGRADE = False

# Databases configuration holds an dictionary with information of the database backend.
# Please refer to the documentation for all examples. http://pypla.net/

if os.environ.get('MYSQL_HOST') is not None:
	DATABASES = {
		'default': {
			'ENGINE': 'peewee_async.MySQLDatabase',
			'NAME': os.getenv('MYSQL_DATABASE', 'pyplanet'),
			'OPTIONS': {
				'host': os.getenv('MYSQL_HOST', 'db'),
				'user': os.getenv('MYSQL_USER', 'pyplanet'),
				'password': os.getenv('MYSQL_PASSWORD', 'pyplanet'),
				'charset': 'utf8mb4',
			}
		}
	}
elif os.environ.get('POSTGRES_HOST') is not None:
        DATABASES = {
                'default': {
                        'ENGINE': 'peewee_async.PostgresqlDatabase',
                        'NAME': os.getenv('POSTGRES_DB', 'pyplanet'),
                        'OPTIONS': {
                                'host': os.getenv('POSTGRES_HOST', 'db'),
                                'user': os.getenv('POSTGRES_USER', 'pyplanet'),
                                'password': os.getenv('POSTGRES_PASSWORD', 'pyplanet'),
                                'autocommit': 'True',
                        }
                }
        }

# Dedicated configuration holds the different dedicated servers that the instances will run on including the names of
# the instances.
DEDICATED = {
	'default': {
		'HOST': os.getenv('MANIAPLANET_HOST', 'dedicated'),
		'PORT': os.getenv('MANIAPLANET_PORT', '5000'),
		'USER': os.getenv('MANIAPLANET_USER', 'SuperAdmin'),
		'PASSWORD': os.getenv('MANIAPLANET_PASSWORD', 'SuperAdmin'),
	}
}

# Map configuration is a set of configuration options related to match settings etc.
# Matchsettings filename.
MAP_MATCHSETTINGS = {
	'default': 'maplist.txt',
}

# Blacklist file is managed by the dedicated server and will be loaded and writen to by PyPlanet once a
# player gets blacklisted. The default will be the filename Maniaplanet always uses and is generic.
BLACKLIST_FILE = {
	'default': 'blacklist.txt'
}

# The storage configuration contains the same instance mapping of the dedicated servers and is used
# to access the filesystem on the dedicated server location.
# Please refer to the documentation for more information. http://pypla.net/
STORAGE = {
	'default': {
		'DRIVER': 'pyplanet.core.storage.drivers.local.LocalDriver',
		'OPTIONS': {},
	}
}

# Define any cache backends that can be used by the core and the plugins to cache data.
# This is not yet implemented. As soon as it's implemented you can activate it with the documentation, available on
# http://pypla.net/
# CACHE = {
# 	'default': {
#
# 	}
# }

# Songs is a list of URLs to .ogg files of songs to be played by the music server.
SONGS = {
	'default': []
}
