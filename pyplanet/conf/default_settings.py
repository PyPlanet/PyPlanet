"""
This file contains the default configuration for PyPlanet. All configuration the user provides will override the
following lines declared in this file.
"""
import logging
import tempfile


##########################################
################# CORE ###################
##########################################

# Enable debug mode to get verbose output, not report any errors and dynamically use the DEBUG in your code
# for extra verbosity of logging/output.
PYPLANET_DEBUG = False

# Define the temporary folder to write temporary files to, such as downloaded files that are only required once
# or are only required parsing and can be removed.
PYPLANET_TMP_PATH = tempfile.gettempdir()

# Allow self-upgrading the installation. Disable on shared servers with one installation!
PYPLANET_SELF_UPGRADE = True

##########################################
################## DB ####################
##########################################

# Databases configuration holds an dictionary with information of the database backend.
# Please refer to the documentation for all examples.
PYPLANET_DB_ENGINE = 'peewee_async.MySQLDatabase'
PYPLANET_DB_DATABASE = 'pyplanet'
PYPLANET_DB_CHARSET = 'utf8mb4'
PYPLANET_DB_PORT = 3306
PYPLANET_DB_HOST = 'localhost'


##########################################
################ STORAGE #################
##########################################

PYPLANET_STORAGE_DRIVER = 'pyplanet.core.storage.drivers.local.LocalDriver'
PYPLANET_STORAGE_AUTODETECT = 1


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
		'handlers': ['console', 'console-debug'],
		'level': logging.DEBUG,
	}
}

# Global logging handlers.
LOGGING_WRITE_LOGS = False
LOGGING_ROTATE_LOGS = True
LOGGING_DIRECTORY = 'logs'

# Error reporting
# See documentation for the options, (docs => privacy).
# Options:
# 0 = Don't report any errors or messages.
# 1 = Report errors with only traces.
# 2 = Report errors with traces and server data.
# 3 = Report errors with traces and server data, provide data to contributed apps (only pyplanet team has access).
LOGGING_REPORTING = 3

# Enable usage analytics. On by default. (Will be turned off when DEBUG is true!).
PYPLANET_ANALYTICS = True


##########################################
################# APPS ###################
##########################################
PYPLANET_APPS = [
	'pyplanet.apps.contrib.admin',
	'pyplanet.apps.contrib.jukebox',
	'pyplanet.apps.contrib.karma',
	'pyplanet.apps.contrib.local_records',
	'pyplanet.apps.contrib.dedimania',  # Will be disabled in Shootmania and TM2020 automatically.
	'pyplanet.apps.contrib.players',
	'pyplanet.apps.contrib.info',
	'pyplanet.apps.contrib.mx',
	'pyplanet.apps.contrib.transactions',
	'pyplanet.apps.contrib.sector_times',
	'pyplanet.apps.contrib.clock',
	'pyplanet.apps.contrib.funcmd',

	# Live Ranking App. Useful when playing in Laps, Rounds and all sort of Trackmania game modes.
	'pyplanet.apps.contrib.live_rankings',
	'pyplanet.apps.contrib.ads',

	# Best CP Widget on top of the screen for the Trackmania game.
	'pyplanet.apps.contrib.best_cps',

	# Use chat-based votes instead of the callvotes of the dedicated server with the voting app.
	'pyplanet.apps.contrib.voting',

	# Dynamic Points Limit is meant for Shootmania Royal.
	'pyplanet.apps.contrib.dynamic_points',

	# Waiting Queue. Enable on limited player servers to fairly queue players.
	'pyplanet.apps.contrib.queue',

	# Music Server App. Enable to queue your music together on the server.
	'pyplanet.apps.contrib.music_server',
]

# The following apps are mandatory loaded, and part of the core. This apps are always loaded *BEFORE* all other
# apps are initiated and loaded.
PYPLANET_MANDATORY_APPS = [
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
PYPLANET_SERVER_HOST = '127.0.0.1'
PYPLANET_SERVER_PORT = '5000'
PYPLANET_SERVER_USER = 'SuperAdmin'
PYPLANET_SERVER_PASSWORD = 'SuperAdmin'

# Map configuration is a set of configuration options related to match settings etc.
# Matchsettings filename.
PYPLANET_MATCHSETTINGS = 'maplist.txt'

# Blacklist file is managed by the dedicated server and will be loaded and writen to by PyPlanet once a
# player gets blacklisted. The default will be the filename Maniaplanet always uses and is generic.
PYPLANET_BLACKLIST = 'blacklist.txt'

# Owner, will be granted highest level of admin at initial start and connect.
PYPLANET_OWNER = None
