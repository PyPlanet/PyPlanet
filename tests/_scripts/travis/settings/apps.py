"""
This file contains the apps & apps settings and overrides the default ones that are defined in the core.
Please copy the default file to: apps.py
"""

# In the apps dictionary and array you configure the apps (or plugins) are loaded for specific pools (controllers).
# Be aware that the list will *ALWAYS* be prepended after the mandatory defaults are loaded in place.
# The mandatory defaults are specific per version, refer to the documentation:
APPS = {
	'default': [
		'pyplanet.apps.contrib.admin',
		'pyplanet.apps.contrib.jukebox.app.Jukebox',
		'pyplanet.apps.contrib.karma',
		'pyplanet.apps.contrib.local_records.app.LocalRecords',
		'pyplanet.apps.contrib.dedimania',
		'pyplanet.apps.contrib.players.app.Players',
		'pyplanet.apps.contrib.mapinfo',
		'pyplanet.apps.contrib.mx',
		'pyplanet.apps.contrib.transactions',
		'tests.apps.migration_test.app.MigrationTest',
		'tests.apps.new_import_style',
	],
}
