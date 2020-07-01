from pyplanet.apps.config import AppConfig
from pyplanet.apps.core.trackmania.callbacks import finish


class TrackmaniaConfig(AppConfig):
	name = 'pyplanet.apps.core.trackmania'
	core = True

	app_dependencies = [
		'core.maniaplanet'
	]

	game_dependencies = [
		'trackmania', 'trackmania_next'
	]

	async def on_start(self):
		self.context.signals.register_signal(finish)
