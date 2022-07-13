import asyncio

from pyplanet.apps.config import AppConfig
from pyplanet.apps.core.trackmania.callbacks import finish, finish_royal_section


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
		self.context.signals.register_signal(finish_royal_section)

		# TM2020 Checkpoint data enabler.
		if self.instance.game.game == 'tmnext':
			await asyncio.gather(
				self.instance.gbx.script('Trackmania.Event.SetCurRaceCheckpointsMode', 'always', encode_json=False, response_id=False),
				self.instance.gbx.script('Trackmania.Event.SetCurLapCheckpointsMode', 'always', encode_json=False, response_id=False)
			)

			self.instance.signals.listen('maniaplanet:match_begin', self.match_begin_royal)

			if await self.instance.mode_manager.get_current_script() == 'Trackmania/TM_RoyalTimeAttack_Online':
				# Reset game, restart map.
				await self.instance.gbx('RestartMap')

	async def match_begin_royal(self, **kwargs):
		"""
		Handle royal match begin callback.
		"""
		if await self.instance.mode_manager.get_current_script() == 'Trackmania/TM_RoyalTimeAttack_Online':
			for player in self.instance.player_manager.online:
				player.flow.handle_match_begin_royal()
