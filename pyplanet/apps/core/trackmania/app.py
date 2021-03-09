import asyncio

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

		# TM2020 Checkpoint data enabler.
		if self.instance.game.game == 'tmnext':
			await asyncio.gather(
				self.instance.gbx.script('Trackmania.Event.SetCurRaceCheckpointsMode', 'always', encode_json=False, response_id=False),
				self.instance.gbx.script('Trackmania.Event.SetCurLapCheckpointsMode', 'always', encode_json=False, response_id=False)
			)
