from pyplanet.apps.config import AppConfig


class ShootmaniaConfig(AppConfig):
	name = 'pyplanet.apps.core.shootmania'
	core = True

	app_dependencies = [
		'core.maniaplanet'
	]

	game_dependencies = [
		'shootmania'
	]
