"""
This file contains the local settings and overrides the default ones.
"""
import os
import tempfile


# Enable debug mode to get verbose output, not report any errors and dynamically use the DEBUG in your code
# for extra verbosity of logging/output.
DEBUG = bool(os.environ.get('PYPLANET_DEBUG', False))

# Owners are logins of the server owners, the owners always get *ALL* the permissions in the system.
OWNERS = []

# Databases configuration holds an dictionary with information of the database backend.
# Please refer to the documentation for all examples.
DATABASES = {}

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
		'DRIVER': 'pyplanet.storage.backends.local',
		'PATH': False
		# Auto-detected by communicating to the dedicated server.
	}
}

# Define any cache backends that can be used by the core and the plugins to cache data.
CACHES = {}
