"""
This file contains the default configuration for PyPlanet. All configuration the user provides will override the
following lines declared in this file.
"""
import tempfile
import os
import logging


##########################################
################# CORE ###################
##########################################

# Enable debug mode to get verbose output, not report any errors and dynamically use the DEBUG in your code
# for extra verbosity of logging/output.
DEBUG = False

# This should ALWAYS be overriden by the local settings.
ROOT_PATH = None

# Define the temporary folder to write temporary files to, such as downloaded files that are only required once
# or are only required parsing and can be removed.
# This should ALWAYS be overriden by the local settings.
TMP_PATH = None

# Add your pools (the controller instances per dedicated here) or leave as it is to use a single instance only.
POOLS = [
	'default'
]

##########################################
################## DB ####################
##########################################

# Databases configuration holds an dictionary with information of the database backend.
# Please refer to the documentation for all examples.
DATABASES = {
	'default': {
		'ENGINE': 'peewee.SqliteDatabase',
		'NAME': 'database.db',
	}
}


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
LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'filters': {
		'require_debug_false': {
			'()': 'pyplanet.utils.log.RequireDebugFalse',
		},
		'require_debug_true': {
			'()': 'pyplanet.utils.log.RequireDebugTrue',
		},
		'require_exception': {
			'()': 'pyplanet.utils.log.RequireException',
		}
	},
	'formatters': {
		'colored': {
			'()': 'colorlog.ColoredFormatter',
			'format': "%(log_color)s%(levelname)-8s%(reset)s %(yellow)s[%(threadName)s][%(name)s]%(reset)s %(white)s%(message)s",
		},
		'timestamped': {
			'format': '[%(asctime)s][%(levelname)s][%(threadName)s] %(name)s: %(message)s (%(filename)s:%(lineno)d)',
		},
	},
	'handlers': {
		'console-debug': {
			'class': 'logging.StreamHandler',
			'filters': ['require_debug_true'],
			'formatter': 'colored',
			'level': logging.DEBUG,
		},
		'console': {
			'class': 'logging.StreamHandler',
			'filters': ['require_debug_false'],
			'formatter': 'colored',
			'level': logging.INFO,
		}
	},
	'loggers': {
		'pyplanet': {
			'handlers': ['console', 'console-debug'],
			'level': logging.DEBUG,
			'propagate': False,
		}
	},
	'root': {
		'handlers': ['console', 'console-debug'],  # TODO: Add file (rotating) logger.
		'level': logging.DEBUG,
	}
}

# Error reporting
# See documentation for the options, (docs => privacy).
# Options:
# 0 = Don't report any errors or messages.
# 1 = Report errors with only traces.
# 2 = Report errors with traces and server data.
# 3 = Report errors with traces and server data, provide data to contributed apps (only pyplanet team has access).
LOGGING_REPORTING = 3

# Enable usage analytics. On by default. (Will be turned off when DEBUG is true!).
ANALYTICS = True


##########################################
################# APPS ###################
##########################################
APPS = {
	'default': []
}

# The following apps are mandatory loaded, and part of the core. This apps are always loaded *BEFORE* all other
# apps are initiated and loaded.
MANDATORY_APPS = [
	'pyplanet.apps.core.pyplanet.app.PyPlanetConfig',
	'pyplanet.apps.core.maniaplanet.app.ManiaplanetConfig',
	'pyplanet.apps.core.trackmania.app.TrackmaniaConfig',
	'pyplanet.apps.core.shootmania.app.ShootmaniaConfig',
	'pyplanet.apps.core.statistics.app.StatisticsConfig',
]

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

# Map configuration is a set of configuration options related to match settings etc.
# Matchsettings filename.
MAP_MATCHSETTINGS = {
	'default': 'maplist.txt'
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

# Owners are logins of the server owners, the owners always get *ALL* the permissions in the system.
OWNERS = {
	'default': []
}
