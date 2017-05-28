"""
Sector Times.
"""
import asyncio

from pyplanet.apps.config import AppConfig
from pyplanet.apps.contrib.sector_times.views import SectorTimesWidget
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.core.signals import pyplanet_start_after


class SectorTimes(AppConfig):
	game_dependencies = ['trackmania']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.widget = SectorTimesWidget(self)

	async def on_start(self):
		self.instance.signal_manager.listen(mp_signals.player.player_connect, self.player_connect)
		self.instance.signal_manager.listen(mp_signals.map.map_start, self.map_start)
		self.instance.signal_manager.listen(mp_signals.flow.podium_start, self.podium_start)

		self.instance.signal_manager.listen(pyplanet_start_after, self.on_after_start)

	async def on_after_start(self, *args, **kwargs):
		await asyncio.sleep(1)
		asyncio.ensure_future(asyncio.gather(*[
			self.player_connect(p) for p in self.instance.player_manager.online
		]))

	async def player_connect(self, player, **kwargs):
		await self.widget.display(player)

	async def map_start(self, *args, **kwargs):
		await asyncio.sleep(2)
		await self.widget.display()

	async def podium_start(self, *args, **kwargs):
		await self.widget.hide()
