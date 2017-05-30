from pyplanet.apps.config import AppConfig
from pyplanet.apps.core.trackmania.callbacks import finish


class TrackmaniaConfig(AppConfig):
	name = 'pyplanet.apps.core.trackmania'
	core = True

	app_dependencies = [
		'core.maniaplanet'
	]

	game_dependencies = [
		'trackmania'
	]

	async def on_start(self):
		self.instance.signal_manager.register_signal(finish)
