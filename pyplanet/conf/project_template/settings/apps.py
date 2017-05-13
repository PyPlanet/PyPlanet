"""
This file contains the apps & apps settings and overrides the default ones that are defined in the core.
Documentation: http://pypla.net/
"""

# In the apps dictionary and array you configure the apps (or plugins) are loaded for specific pools (controllers).
# Be aware that the list will *ALWAYS* be prepended after the mandatory defaults are loaded in place.
# The mandatory defaults are specific per version, refer to the documentation:
# DOCUMENTATION: http://pypla.net/
APPS = {
	'default': [
		'pyplanet.apps.contrib.admin',
		'pyplanet.apps.contrib.jukebox',
		'pyplanet.apps.contrib.karma',
		'pyplanet.apps.contrib.local_records',
		'pyplanet.apps.contrib.dedimania',
		'pyplanet.apps.contrib.players',
		'pyplanet.apps.contrib.mapinfo',
		'pyplanet.apps.contrib.mx',
		'pyplanet.apps.contrib.transactions',
	]
}
