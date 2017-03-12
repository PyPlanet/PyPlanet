"""
This file contains the default configuration for PyPlanet. All configuration the user provides will override the
following lines declared in this file.
"""
import tempfile


##########################################
################# CORE ###################
##########################################

# Enable debug mode to get verbose output, not report any errors and dynamically use the DEBUG in your code
# for extra verbosity of logging/output.
import os

DEBUG = False

# Owners are logins of the server owners, the owners always get *ALL* the permissions in the system.
OWNERS = []

# Define the temporary folder to write temporary files to, such as downloaded files that are only required once
# or are only required parsing and can be removed.
TMP_ROOT = tempfile.tempdir


##########################################
################## DB ####################
##########################################

# Databases configuration holds an dictionary with information of the database backend.
# Please refer to the documentation for all examples.
DATABASES = {}


##########################################
################ CACHE ###################
##########################################

# Define any cache backends that can be used by the core and the plugins to cache data.
CACHES = {
	'default': {
		'DRIVER': 'pyplanet.cache.backends.memory',
	}
}


##########################################
############### LOGGING ##################
##########################################

# Logging configuration handler. Defaults to dictionary configuration.
LOGGING_CONFIG = 'logging.config.dictConfig'

# Logging configuration.
LOGGING = {}


##########################################
############## DEDICATED #################
##########################################

# Dedicated contains the dedicated servers configurations, by default this is the localhost entry with default
# credentials and details.
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
		'DRIVER': 'pyplanet.storage.backends.local',
		'PATH': False
		# Auto-detected by communicating to the dedicated server.
	}
}
