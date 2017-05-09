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
		'pyplanet.apps.contrib.admin.app.Admin',
		'pyplanet.apps.contrib.jukebox.app.Jukebox',
		'pyplanet.apps.contrib.karma.app.Karma',
		'pyplanet.apps.contrib.local_records.app.LocalRecords',
		'pyplanet.apps.contrib.dedimania.app.Dedimania',
		'pyplanet.apps.contrib.players.app.Players',
		'pyplanet.apps.contrib.mapinfo.app.MapInfo',
		'pyplanet.apps.contrib.mx.app.MX',
	]
}
