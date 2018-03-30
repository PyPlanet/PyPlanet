"""
This file contains the apps & apps settings and overrides the default ones that are defined in the core.
Documentation: http://pypla.net/

If you want to use other configuration methods like YAML or JSON files, take a look at http://pypla.net/ and head to the
configuration pages.
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
		'pyplanet.apps.contrib.dedimania',  # Will be disabled in Shootmania automatically.
		'pyplanet.apps.contrib.players',
		'pyplanet.apps.contrib.info',
		'pyplanet.apps.contrib.mx',
		'pyplanet.apps.contrib.transactions',
		'pyplanet.apps.contrib.sector_times',
		'pyplanet.apps.contrib.clock',

		# You can optionally enable one of the following apps. Please look at this page for more information:
		# http://pypla.net/#app-docs

		# Live Ranking App. Useful when playing in Laps, Rounds and all sort of Trackmania game modes.
		'pyplanet.apps.contrib.live_rankings',

		# Best CP Widget on top of the screen for the Trackmania game.
		'pyplanet.apps.contrib.best_cps',

		# Use chat-based votes instead of the callvotes of the dedicated server with the voting app.
		'pyplanet.apps.contrib.voting',

		# Dynamic Points Limit is meant for Shootmania Royal.
		# 'pyplanet.apps.contrib.dynamic_points',

		# Waiting Queue. Enable on limited player servers to fairly queue players.
		# 'pyplanet.apps.contrib.queue',

		# Music Server App. Enable to queue your music together on the server.
		# 'pyplanet.apps.contrib.music_server',
	]
}
