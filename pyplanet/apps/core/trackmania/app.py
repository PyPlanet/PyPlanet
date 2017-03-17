from pyplanet.apps.config import AppConfig


class TrackmaniaConfig(AppConfig):
	name = 'pyplanet.apps.core.trackmania'
	core = True

	app_dependencies = [
		'core.maniaplanet'
	]

	game_dependencies = [
		'trackmania'
	]
